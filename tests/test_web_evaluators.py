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

    def test_vinculo_explicito_e_associacao_auditada_de_legados_web027(self) -> None:
        """WEB-027: Testa vinculo explicito auditado de entidades legadas (REQ-AUD-002 / REQ-PAR-005)."""
        from uuid import uuid4

        # 1. Cria paciente e avaliador centrais
        pat_res = self.h.importer.post("/api/v1/patients", json={"full_name": "Paciente Central Legado"})
        self.assertEqual(pat_res.status_code, 201)
        pat = pat_res.json()

        ev_res = self.h.importer.post("/api/v1/evaluators", json={"full_name": "Avaliador Central Legado"})
        self.assertEqual(ev_res.status_code, 201)
        ev = ev_res.json()

        # 2. Cria participante pseudonimizado legado anterior a CHG-005 (sem patient_id)
        legacy_part_uuid = str(uuid4())
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                """INSERT INTO web_project_participants (participant_uuid, project_id, pseudonym, patient_id)
                   VALUES (%s, %s, 'PSEUDO_LEGADO_001', NULL)""",
                (legacy_part_uuid, self.h.project_id),
            )

        # 3. Comprova que coincidencia textual NAO unifica automaticamente
        with psycopg.connect(self.database_url) as conn:
            part_check = conn.execute(
                "SELECT patient_id FROM web_project_participants WHERE participant_uuid = %s",
                (legacy_part_uuid,),
            ).fetchone()[0]
            self.assertIsNone(part_check, "Participante legado nao deve ser associado automaticamente.")

        # 4. Perfil sem permissao (consulta) e recusado ao tentar associar legado
        forbidden_link = self.h.consulta.post(
            "/api/v1/admin/legacy-links",
            json={
                "entity_type": "patient",
                "legacy_participant_uuid": legacy_part_uuid,
                "patient_id": pat["id"],
                "reason_code": "MIGRACAO_AUDITADA_HISTORICA",
            },
        )
        self.assertEqual(forbidden_link.status_code, 403)

        # 5. Administrador realiza vinculo explicito de participante legado a paciente central
        link_pat_res = self.h.admin.post(
            "/api/v1/admin/legacy-links",
            json={
                "entity_type": "patient",
                "legacy_participant_uuid": legacy_part_uuid,
                "patient_id": pat["id"],
                "reason_code": "MIGRACAO_AUDITADA_HISTORICA",
            },
        )
        self.assertEqual(link_pat_res.status_code, 201, link_pat_res.text)
        link_pat = link_pat_res.json()
        self.assertEqual(link_pat["entity_type"], "patient")
        self.assertEqual(link_pat["patient_id"], pat["id"])
        self.assertTrue(link_pat["active"])

        # Confere que web_project_participants foi atualizado e auditoria gravada
        with psycopg.connect(self.database_url) as conn:
            updated_pid = conn.execute(
                "SELECT patient_id FROM web_project_participants WHERE participant_uuid = %s",
                (legacy_part_uuid,),
            ).fetchone()[0]
            self.assertEqual(str(updated_pid), pat["id"])

            audit_evt = conn.execute(
                """SELECT action, reason_code FROM web_registry_audit_events
                   WHERE entity_type = 'patient' AND entity_id = %s AND action = 'relink'""",
                (pat["id"],),
            ).fetchone()
            self.assertIsNotNone(audit_evt)
            self.assertEqual(audit_evt[1], "MIGRACAO_AUDITADA_HISTORICA")

        # 6. Administrador vincula rotulo textual de avaliador historico a avaliador central
        link_ev_res = self.h.admin.post(
            "/api/v1/admin/legacy-links",
            json={
                "entity_type": "evaluator",
                "legacy_evaluator_label": "E_SINTETICO_LEGADO_2024",
                "evaluator_uuid": ev["id"],
                "reason_code": "RECONCILIACAO_AVALIADOR_AUDITADA",
            },
        )
        self.assertEqual(link_ev_res.status_code, 201, link_ev_res.text)
        link_ev = link_ev_res.json()
        self.assertEqual(link_ev["entity_type"], "evaluator")
        self.assertEqual(link_ev["evaluator_uuid"], ev["id"])

        # 7. Consulta listagem de vinculos legados
        listed = self.h.admin.get("/api/v1/admin/legacy-links").json()
        self.assertGreaterEqual(len(listed["items"]), 2)
        link_ids = {row["link_id"] for row in listed["items"]}
        self.assertIn(link_pat["link_id"], link_ids)
        self.assertIn(link_ev["link_id"], link_ids)

        # 8. Desativacao reversivel de vinculo legado
        deact = self.h.admin.post(
            f"/api/v1/admin/legacy-links/{link_pat['link_id']}/deactivate",
            json={"reason_code": "DESVINCULACAO_SOLICITADA"},
        )
        self.assertEqual(deact.status_code, 200, deact.text)
        self.assertFalse(deact.json()["active"])

        with psycopg.connect(self.database_url) as conn:
            deact_link = conn.execute(
                "SELECT active FROM web_legacy_entity_links WHERE link_id = %s",
                (link_pat["link_id"],),
            ).fetchone()[0]
            self.assertFalse(deact_link)

            cleared_pid = conn.execute(
                "SELECT patient_id FROM web_project_participants WHERE participant_uuid = %s",
                (legacy_part_uuid,),
            ).fetchone()[0]
            self.assertIsNone(cleared_pid, "Desativacao deve limpar patient_id sem exclusao destrutiva.")

            unlink_evt = conn.execute(
                """SELECT action, reason_code FROM web_registry_audit_events
                   WHERE entity_type = 'patient' AND entity_id = %s AND action = 'deactivate'""",
                (pat["id"],),
            ).fetchone()
            self.assertIsNotNone(unlink_evt)
            self.assertEqual(unlink_evt[1], "DESVINCULACAO_SOLICITADA")


if __name__ == "__main__":
    unittest.main()
