"""Testes de dominio, API e PostgreSQL do cadastro central de avaliadores (CAD-01, CAD-03)."""

from __future__ import annotations

import os
import unittest

import psycopg

from stroop.domain.registry import format_evaluator_code
from tests import test_web_sessions as helpers


class WebEvaluatorsPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.database_url = os.environ.get("TEST_DATABASE_URL", "")
        if not cls.database_url:
            raise unittest.SkipTest("TEST_DATABASE_URL nao configurada")
        db_name = psycopg.conninfo.conninfo_to_dict(cls.database_url).get("dbname", "")
        if not db_name.startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco PostgreSQL descartavel obrigatorio")

    def setUp(self) -> None:
        self.h = helpers.WebSessionsPostgresTests()
        self.h.database_url = self.database_url
        self.addCleanup(self.h.doCleanups)
        self.h.setUp()

    def test_crud_avaliador_separacao_conta_login_e_historico_preservado(self) -> None:
        self.assertEqual(format_evaluator_code(12), "EVA-000012")
        with psycopg.connect(self.database_url) as connection:
            users_before = connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0]
            creds_before = connection.execute(
                "SELECT COUNT(*) FROM web_local_credentials"
            ).fetchone()[0]

        created = self.h.importer.post(
            "/api/v1/evaluators",
            json={"full_name": "  Prof.  Roberto   Almeida  Sintético "},
        )
        self.assertEqual(created.status_code, 201, created.text)
        evaluator = created.json()
        self.assertRegex(evaluator["evaluator_code"], r"^EVA-\d{6,}$")
        self.assertEqual(evaluator["full_name"], "Prof. Roberto Almeida Sintético")
        self.assertEqual(evaluator["initials"], "PRAS")
        self.assertTrue(evaluator["active"])

        # Criar avaliador nunca cria conta de login em app_users ou web_local_credentials
        with psycopg.connect(self.database_url) as connection:
            users_after = connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0]
            creds_after = connection.execute(
                "SELECT COUNT(*) FROM web_local_credentials"
            ).fetchone()[0]
        self.assertEqual(users_after, users_before)
        self.assertEqual(creds_after, creds_before)

        # Duplicidade de avaliador bloqueada sem confirm_homonym=true
        conflict = self.h.importer.post(
            "/api/v1/evaluators",
            json={"full_name": "prof. roberto almeida sintetico"},
        )
        self.assertEqual(conflict.status_code, 409, conflict.text)
        self.assertEqual(conflict.json()["error"]["code"], "duplicate_candidate_found")

        # Homonimo confirmado cria novo registro com EVA-... distinto
        homonym = self.h.importer.post(
            "/api/v1/evaluators",
            json={
                "full_name": "Prof. Roberto Almeida Sintetico",
                "initials": "RAS2",
                "confirm_homonym": True,
            },
        )
        self.assertEqual(homonym.status_code, 201, homonym.text)
        self.assertNotEqual(homonym.json()["evaluator_code"], evaluator["evaluator_code"])

        # Executa sessao completa vinculada ao avaliador e paciente cadastrados
        patient = self.h.importer.post(
            "/api/v1/patients",
            json={"full_name": "Paciente Avaliado Sintético", "initials": "PAS"},
        ).json()
        inv = self.h.importer.post(
            f"/api/v1/projects/{self.h.project_id}/invitations",
            json={
                "patient_id": patient["id"],
                "evaluator_id": evaluator["id"],
                "visit": "T1",
                "test_code": "stroop_go_nogo_ptbr",
                "initials": "PAS",
            },
        )
        self.assertEqual(inv.status_code, 201, inv.text)
        issued = inv.json()

        participant = self.h._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post("/api/v1/participant/redeem", json={"code": issued["code"]})
        self.assertEqual(redeemed.status_code, 201, redeemed.text)
        participant.headers["X-CSRF-Token"] = redeemed.json()["csrf_token"]
        bootstrap = participant.get("/api/v1/participant/session").json()
        # O bootstrap do participante nao expoe dados nominais
        self.assertNotIn("Paciente Avaliado Sintético", str(bootstrap))
        self.assertNotIn("Prof. Roberto Almeida Sintético", str(bootstrap))

        started = participant.post(
            "/api/v1/participant/start",
            json={"app_version": "synthetic-web-0.1.0"},
        )
        self.assertEqual(started.status_code, 200, started.text)
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "UPDATE web_participant_sessions SET started_at = clock_timestamp() - interval '61 seconds' WHERE session_id = %s",
                (issued["session_id"],),
            )
        trials = []
        for idx, cond in enumerate(bootstrap["main_conditions"]):
            start_ms = idx * 3750
            responds = cond["condition_id"] % 2 == 0
            trials.append(
                {
                    "trial_number": idx + 1,
                    "condition_id": cond["condition_id"],
                    "key_pressed": "space" if responds else None,
                    "reaction_time_ms": 512.25 if responds else None,
                    "trial_start_ms": start_ms,
                    "stimulus_onset_ms": start_ms + 300,
                    "stimulus_offset_ms": start_ms + 2800,
                    "trial_end_ms": start_ms + 3750,
                    "key_at_ms": start_ms + 812.25 if responds else None,
                }
            )
        completed = participant.post(
            "/api/v1/participant/complete",
            json={
                "protocol_id": bootstrap["protocol_id"],
                "test_version": bootstrap["test_version"],
                "platform": "web",
                "app_version": "synthetic-web-0.1.0",
                "frame_period_ms": 16,
                "trials": trials,
            },
        )
        self.assertEqual(completed.status_code, 201, completed.text)
        assessment_id = completed.json()["assessment_id"]

        # Confere separacao entre issued_by (conta autenticada) e evaluator_uuid/evaluator_code
        with psycopg.connect(self.database_url) as connection:
            inv_row = connection.execute(
                """SELECT evaluator_issuer, evaluator_subject, evaluator_uuid, evaluator_id, patient_id
                   FROM web_invitations WHERE invitation_id = %s""",
                (issued["invitation_id"],),
            ).fetchone()
            self.assertEqual(inv_row[0], helpers.ISSUER)
            self.assertEqual(inv_row[1], helpers.IMPORTER)
            self.assertEqual(str(inv_row[2]), evaluator["id"])
            self.assertEqual(inv_row[3], evaluator["evaluator_code"])
            self.assertEqual(str(inv_row[4]), patient["id"])

            assess_row = connection.execute(
                """SELECT a.participant_id, a.participant_name, a.initials, a.evaluator,
                          wa.patient_id, wa.evaluator_uuid
                   FROM assessments a
                   JOIN web_assessments wa USING (assessment_id)
                   WHERE a.assessment_id = %s""",
                (assessment_id,),
            ).fetchone()
            self.assertEqual(assess_row[0], patient["participant_code"])
            self.assertEqual(assess_row[1], "NAO_COLETADO")
            self.assertIsNone(assess_row[2])
            self.assertEqual(assess_row[3], evaluator["evaluator_code"])
            self.assertEqual(str(assess_row[4]), patient["id"])
            self.assertEqual(str(assess_row[5]), evaluator["id"])

            # ON DELETE RESTRICT bloqueia exclusao fisica do avaliador
            with self.assertRaises(psycopg.errors.ForeignKeyViolation):
                connection.execute(
                    "DELETE FROM web_evaluators WHERE id = %s",
                    (evaluator["id"],),
                )

        # Inativar avaliador bloqueia novas preparacoes (409 state_conflict), mantendo historico
        deactivated = self.h.importer.patch(
            f"/api/v1/evaluators/{evaluator['id']}",
            json={"active": False, "reason_code": "afastamento_temporario"},
        )
        self.assertEqual(deactivated.status_code, 200, deactivated.text)
        self.assertFalse(deactivated.json()["active"])

        blocked_inv = self.h.importer.post(
            f"/api/v1/projects/{self.h.project_id}/invitations",
            json={
                "patient_id": patient["id"],
                "evaluator_id": evaluator["id"],
                "visit": "T2",
            },
        )
        self.assertEqual(blocked_inv.status_code, 409, blocked_inv.text)
        self.assertEqual(blocked_inv.json()["error"]["code"], "state_conflict")

        # Ficha do avaliador preserva historico de avaliacoes conduzidas e auditoria
        ev_detail = self.h.consulta.get(f"/api/v1/evaluators/{evaluator['id']}")
        self.assertEqual(ev_detail.status_code, 200, ev_detail.text)
        self.assertEqual(ev_detail.json()["assessment_count"], 1)
        self.assertEqual(ev_detail.json()["instruments"], ["stroop_go_nogo_ptbr"])
        self.assertEqual(
            ev_detail.json()["assessments"][0]["assessment_id"],
            assessment_id,
        )
        self.assertEqual(
            [item["action"] for item in ev_detail.json()["audit_history"]],
            ["deactivate", "create"],
        )

    def test_revinculacao_auditada_avaliador_e_controles(self) -> None:
        ev1 = self.h.importer.post(
            "/api/v1/evaluators",
            json={"full_name": "Dr. Avaliador Inicial Errado", "initials": "AIE"},
        ).json()
        ev2 = self.h.importer.post(
            "/api/v1/evaluators",
            json={"full_name": "Dra. Avaliadora Destino Correta", "initials": "ADC"},
        ).json()
        patient = self.h.importer.post(
            "/api/v1/patients",
            json={"full_name": "Paciente da Avaliação", "initials": "PA"},
        ).json()

        inv = self.h.importer.post(
            f"/api/v1/projects/{self.h.project_id}/invitations",
            json={
                "patient_id": patient["id"],
                "evaluator_id": ev1["id"],
                "visit": "V1",
                "test_code": "stroop_go_nogo_ptbr",
                "initials": "PA",
            },
        ).json()

        participant = self.h._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post("/api/v1/participant/redeem", json={"code": inv["code"]})
        self.assertEqual(redeemed.status_code, 201, redeemed.text)
        participant.headers["X-CSRF-Token"] = redeemed.json()["csrf_token"]
        bootstrap = participant.get("/api/v1/participant/session").json()
        started = participant.post(
            "/api/v1/participant/start",
            json={"app_version": "synthetic-web-0.1.0"},
        )
        self.assertEqual(started.status_code, 200, started.text)
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "UPDATE web_participant_sessions SET started_at = clock_timestamp() - interval '61 seconds' WHERE session_id = %s",
                (inv["session_id"],),
            )
        trials = [
            {
                "trial_number": idx + 1,
                "condition_id": cond["condition_id"],
                "key_pressed": "space" if cond["condition_id"] % 2 == 0 else None,
                "reaction_time_ms": 500.0 if cond["condition_id"] % 2 == 0 else None,
                "trial_start_ms": idx * 3750,
                "stimulus_onset_ms": idx * 3750 + 300,
                "stimulus_offset_ms": idx * 3750 + 2800,
                "trial_end_ms": idx * 3750 + 3750,
                "key_at_ms": idx * 3750 + 800.0 if cond["condition_id"] % 2 == 0 else None,
            }
            for idx, cond in enumerate(bootstrap["main_conditions"])
        ]
        completed = participant.post(
            "/api/v1/participant/complete",
            json={
                "protocol_id": bootstrap["protocol_id"],
                "test_version": bootstrap["test_version"],
                "platform": "web",
                "app_version": "synthetic-web-0.1.0",
                "frame_period_ms": 16,
                "trials": trials,
            },
        )
        self.assertEqual(completed.status_code, 201, completed.text)
        assessment_id = completed.json()["assessment_id"]

        # Executa revinculacao auditada para ev2
        relink_resp = self.h.importer.post(
            f"/api/v1/projects/{self.h.project_id}/assessments/{assessment_id}/relink",
            json={
                "evaluator_id": ev2["id"],
                "reason_code": "correcao_erro_humano_avaliador",
            },
        )
        self.assertEqual(relink_resp.status_code, 200, relink_resp.text)
        relink_data = relink_resp.json()
        self.assertEqual(relink_data["assessment_id"], assessment_id)
        self.assertEqual(relink_data["evaluator_id"], ev2["id"])
        self.assertTrue(relink_data["relinked"])

        # Confere atualizacao nas tabelas
        with psycopg.connect(self.database_url) as connection:
            wa_row = connection.execute(
                "SELECT evaluator_uuid FROM web_assessments WHERE assessment_id = %s",
                (assessment_id,),
            ).fetchone()
            self.assertEqual(str(wa_row[0]), ev2["id"])

            a_row = connection.execute(
                "SELECT evaluator FROM assessments WHERE assessment_id = %s",
                (assessment_id,),
            ).fetchone()
            self.assertEqual(a_row[0], ev2["evaluator_code"])

            inv_row = connection.execute(
                "SELECT evaluator_uuid, evaluator_id FROM web_invitations WHERE invitation_id = %s",
                (inv["invitation_id"],),
            ).fetchone()
            self.assertEqual(str(inv_row[0]), ev2["id"])
            self.assertEqual(inv_row[1], ev2["evaluator_code"])

            audit_events = connection.execute(
                """SELECT entity_id, action, reason_code FROM web_registry_audit_events
                   WHERE action = 'relink' AND entity_type = 'invitation_link'
                   ORDER BY occurred_at ASC""",
            ).fetchall()
            self.assertGreaterEqual(len(audit_events), 2)
            entity_ids = {str(row[0]) for row in audit_events}
            self.assertIn(ev1["id"], entity_ids)
            self.assertIn(ev2["id"], entity_ids)

        # Ficha do ev2 exibe a avaliacao
        detail_ev2 = self.h.consulta.get(f"/api/v1/evaluators/{ev2['id']}").json()
        self.assertEqual(detail_ev2["assessment_count"], 1)
        self.assertEqual(detail_ev2["assessments"][0]["assessment_id"], assessment_id)
        self.assertIn("relink", [ev["action"] for ev in detail_ev2["audit_history"]])

        # Ficha do ev1 nao tem mais a avaliacao, mas tem o relink auditado
        detail_ev1 = self.h.consulta.get(f"/api/v1/evaluators/{ev1['id']}").json()
        self.assertEqual(detail_ev1["assessment_count"], 0)
        self.assertIn("relink", [ev["action"] for ev in detail_ev1["audit_history"]])


if __name__ == "__main__":
    unittest.main()
