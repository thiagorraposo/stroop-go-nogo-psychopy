"""Testes de dominio, API e PostgreSQL do cadastro central de pacientes (CAD-01, CAD-02)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
import os
import unittest
from uuid import uuid4

import psycopg

from stroop.domain.registry import (
    InvalidRegistryDataError,
    derive_initials,
    format_patient_code,
    normalize_person_name,
    validate_disambiguation_note,
    validate_initials,
    validate_reason_code,
    validate_test_code,
)
from tests import test_web_sessions as helpers


class PatientDomainTests(unittest.TestCase):
    def test_normalizacao_nome_iniciais_e_codigo_pat(self) -> None:
        cleaned, normalized = normalize_person_name("  João   da   Conceição  Ávila ")
        self.assertEqual(cleaned, "João da Conceição Ávila")
        self.assertEqual(normalized, "joao da conceicao avila")
        self.assertEqual(derive_initials(cleaned), "JCA")
        self.assertEqual(validate_initials(None, fallback_name=cleaned), "JCA")
        self.assertEqual(validate_initials("  J.C.A. "), "J.C.A.")
        self.assertEqual(
            format_patient_code(date(2026, 11, 7), 1),
            "PAT-20261107-000001",
        )
        self.assertEqual(
            validate_disambiguation_note("  Coorte sintética A "),
            "Coorte sintética A",
        )
        self.assertEqual(validate_reason_code(" correcao_ortografica "), "correcao_ortografica")
        self.assertEqual(
            validate_test_code(None)["test_code"],
            "stroop_go_nogo_ptbr",
        )

    def test_rejeita_entradas_invalidas_de_dominio(self) -> None:
        for invalid_name in ("", "A", "   ", "A" * 121, "Nome\nInvalido", 123):
            with self.subTest(name=invalid_name), self.assertRaises(InvalidRegistryDataError):
                normalize_person_name(invalid_name)
        for invalid_initials in ("A" * 17, "AB\x00", 123):
            with self.subTest(initials=invalid_initials), self.assertRaises(InvalidRegistryDataError):
                validate_initials(invalid_initials)
        for invalid_note in ("X" * 161, "Nota\rInvalida", 99):
            with self.subTest(note=invalid_note), self.assertRaises(InvalidRegistryDataError):
                validate_disambiguation_note(invalid_note)
        for invalid_reason in ("", "   ", "R" * 121, "motivo\n", None):
            with self.subTest(reason=invalid_reason), self.assertRaises(InvalidRegistryDataError):
                validate_reason_code(invalid_reason)
        with self.assertRaises(InvalidRegistryDataError):
            validate_test_code("instrumento_inexistente")


@unittest.skipUnless(os.environ.get("TEST_DATABASE_URL"), "TEST_DATABASE_URL nao configurada")
class WebPatientsPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.database_url = os.environ["TEST_DATABASE_URL"]
        db_name = psycopg.conninfo.conninfo_to_dict(cls.database_url).get("dbname", "")
        if not db_name.startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco PostgreSQL descartavel obrigatorio")

    def setUp(self) -> None:
        self.h = helpers.WebSessionsPostgresTests()
        self.h.database_url = self.database_url
        self.addCleanup(self.h.doCleanups)
        self.h.setUp()

    def test_crud_paciente_homonimos_auditoria_e_autorizacao(self) -> None:
        created = self.h.importer.post(
            "/api/v1/patients",
            json={
                "full_name": "  Helena   Conceição  Sintética ",
                "disambiguation_note": "Unidade sintética 01",
            },
        )
        self.assertEqual(created.status_code, 201, created.text)
        patient = created.json()
        self.assertRegex(patient["participant_code"], r"^PAT-\d{8}-\d{6,}$")
        self.assertEqual(patient["full_name"], "Helena Conceição Sintética")
        self.assertEqual(patient["initials"], "HCS")
        self.assertEqual(patient["disambiguation_note"], "Unidade sintética 01")
        self.assertFalse(patient["is_homonym_confirmed"])
        self.assertTrue(patient["active"])

        # Busca fonetica/sem acento de duplicidades antes do cadastro
        dup_check = self.h.importer.get(
            "/api/v1/patients/duplicates",
            params={"full_name": "helena conceicao sintetica", "initials": "HCS"},
        )
        self.assertEqual(dup_check.status_code, 200, dup_check.text)
        candidates = dup_check.json()["candidates"]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["id"], patient["id"])
        self.assertTrue(candidates[0]["exact_match"])

        # Tentativa de duplicacao sem confirm_homonym=true retorna 409 duplicate_candidate_found
        conflict = self.h.importer.post(
            "/api/v1/patients",
            json={"full_name": "Helena Conceicao Sintetica"},
        )
        self.assertEqual(conflict.status_code, 409, conflict.text)
        self.assertEqual(
            conflict.json()["error"]["code"],
            "duplicate_candidate_found",
        )
        self.assertEqual(conflict.json()["candidates"][0]["id"], patient["id"])

        # Confirmacao explicita de homonimo cria segundo paciente com codigo distinto
        homonym = self.h.importer.post(
            "/api/v1/patients",
            json={
                "full_name": "Helena Conceicao Sintetica",
                "initials": "HCS2",
                "disambiguation_note": "Homonimo confirmado lote B",
                "confirm_homonym": True,
            },
        )
        self.assertEqual(homonym.status_code, 201, homonym.text)
        homonym_data = homonym.json()
        self.assertNotEqual(homonym_data["id"], patient["id"])
        self.assertNotEqual(homonym_data["participant_code"], patient["participant_code"])
        self.assertTrue(homonym_data["is_homonym_confirmed"])

        # Listagem e busca por nome sem acento, codigo ou iniciais
        listed = self.h.consulta.get(
            "/api/v1/patients",
            params={"search": "conceicao", "sort": "code_asc"},
        )
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(listed.json()["total"], 2)

        by_code = self.h.consulta.get(
            "/api/v1/patients",
            params={"search": patient["participant_code"]},
        )
        self.assertEqual(by_code.status_code, 200, by_code.text)
        self.assertEqual(len(by_code.json()["items"]), 1)
        self.assertEqual(by_code.json()["items"][0]["id"], patient["id"])

        # Edicao cadastral auditada e inativacao logica
        updated = self.h.importer.patch(
            f"/api/v1/patients/{patient['id']}",
            json={
                "full_name": "Helena Conceição Sintética Retificada",
                "initials": "HCSR",
                "reason_code": "correcao_ortografica",
            },
        )
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()["id"], patient["id"])
        self.assertEqual(updated.json()["participant_code"], patient["participant_code"])
        self.assertEqual(updated.json()["full_name"], "Helena Conceição Sintética Retificada")
        self.assertEqual(updated.json()["initials"], "HCSR")

        deactivated = self.h.importer.patch(
            f"/api/v1/patients/{patient['id']}",
            json={"active": False, "reason_code": "inativacao_operacional"},
        )
        self.assertEqual(deactivated.status_code, 200, deactivated.text)
        self.assertFalse(deactivated.json()["active"])

        detail = self.h.consulta.get(f"/api/v1/patients/{patient['id']}")
        self.assertEqual(detail.status_code, 200, detail.text)
        actions = [event["action"] for event in detail.json()["audit_history"]]
        self.assertEqual(actions, ["deactivate", "update", "create"])

        # Controles negativos de autorizacao e CSRF
        self.assertEqual(
            self.h.consulta.post(
                "/api/v1/patients",
                json={"full_name": "Paciente Nao Autorizado"},
            ).status_code,
            403,
        )
        self.assertEqual(
            self.h.consulta.get(
                "/api/v1/patients/duplicates",
                params={"full_name": "Helena"},
            ).status_code,
            403,
        )
        self.assertEqual(self.h.outsider.get("/api/v1/patients").status_code, 403)
        self.assertEqual(
            self.h.importer.post(
                "/api/v1/patients",
                json={"full_name": "Sem CSRF"},
                headers={"X-CSRF-Token": "invalid"},
            ).status_code,
            403,
        )

    def test_geracao_concorrente_sem_colisao_e_reutilizacao_entre_projetos_e_visitas(self) -> None:
        def register_index(idx: int) -> str:
            with psycopg.connect(self.database_url) as _:
                pass
            from stroop.application import web_registry
            from stroop.domain.auth import AppUser

            actor = AppUser(helpers.ISSUER, helpers.IMPORTER, None, "importacao", True)
            created = web_registry.create_patient(
                self.database_url,
                actor,
                full_name=f"Participante Concorrente Sintetico {idx:02d}",
                initials=f"PC{idx:02d}",
            )
            return created["participant_code"]

        with ThreadPoolExecutor(max_workers=4) as executor:
            codes = list(executor.map(register_index, range(1, 9)))
        self.assertEqual(len(set(codes)), 8)

        # Criacao de paciente e avaliador para reutilizacao em 2 projetos e 2 visitas
        patient = self.h.importer.post(
            "/api/v1/patients",
            json={"full_name": "Carlos Eduardo Sintético", "initials": "CES"},
        ).json()
        evaluator = self.h.importer.post(
            "/api/v1/evaluators",
            json={"full_name": "Dra. Marina Avaliadora Sintética", "initials": "MAS"},
        ).json()

        second_project = self.h.admin.post(
            "/api/v1/projects",
            json={"code": "SYNTHETIC_WEB_2", "name": "Segundo Projeto Sintetico"},
        ).json()["id"]
        self.h.admin.put(
            f"/api/v1/projects/{second_project}/members/{helpers.opaque_user_id(helpers.ISSUER, helpers.IMPORTER)}",
            json={"active": True},
        )

        for proj_id, visit in (
            (self.h.project_id, "T1"),
            (self.h.project_id, "T2"),
            (second_project, "T1"),
        ):
            inv = self.h.importer.post(
                f"/api/v1/projects/{proj_id}/invitations",
                json={
                    "patient_id": patient["id"],
                    "evaluator_id": evaluator["id"],
                    "visit": visit,
                    "test_code": "stroop_go_nogo_ptbr",
                    "initials": patient["initials"],
                },
            )
            self.assertEqual(inv.status_code, 201, inv.text)
            self.assertEqual(
                inv.json()["summary"]["participant_code"],
                patient["participant_code"],
            )
            self.assertEqual(
                inv.json()["summary"]["evaluator_code"],
                evaluator["evaluator_code"],
            )

        # Consulta por usuario vinculado apenas ao primeiro projeto (consulta) vs ambos (importer)
        detail_importer = self.h.importer.get(f"/api/v1/patients/{patient['id']}").json()
        self.assertEqual(
            sorted(detail_importer["project_codes"]),
            ["SYNTHETIC_WEB", "SYNTHETIC_WEB_2"],
        )
        self.assertEqual(detail_importer["visit_count"], 3)
        self.assertEqual(len(detail_importer["sessions"]), 3)

        detail_consulta = self.h.consulta.get(f"/api/v1/patients/{patient['id']}").json()
        self.assertEqual(detail_consulta["project_codes"], ["SYNTHETIC_WEB"])
        self.assertEqual(detail_consulta["visit_count"], 2)
        self.assertEqual(len(detail_consulta["sessions"]), 2)
        self.assertEqual(
            self.h.consulta.get(
                "/api/v1/patients",
                params={"project_id": second_project},
            ).status_code,
            404,
        )

        # ON DELETE RESTRICT bloqueia exclusao fisica de paciente referenciado
        with psycopg.connect(self.database_url) as connection:
            with self.assertRaises(psycopg.errors.ForeignKeyViolation):
                connection.execute(
                    "DELETE FROM web_patients WHERE id = %s",
                    (patient["id"],),
                )

    def test_revinculacao_auditada_paciente_e_controles(self) -> None:
        p1 = self.h.importer.post(
            "/api/v1/patients",
            json={"full_name": "Paciente Inicial Errado", "initials": "PIE"},
        ).json()
        p2 = self.h.importer.post(
            "/api/v1/patients",
            json={"full_name": "Paciente Destino Correto", "initials": "PDC"},
        ).json()
        evaluator = self.h.importer.post(
            "/api/v1/evaluators",
            json={"full_name": "Dr. Avaliador Responsável", "initials": "DAR"},
        ).json()

        inv = self.h.importer.post(
            f"/api/v1/projects/{self.h.project_id}/invitations",
            json={
                "patient_id": p1["id"],
                "evaluator_id": evaluator["id"],
                "visit": "V1",
                "test_code": "stroop_go_nogo_ptbr",
                "initials": "PIE",
            },
        ).json()

        # Completa sessao
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

        # Confere vinculo inicial com p1
        with psycopg.connect(self.database_url) as connection:
            wa_row = connection.execute(
                "SELECT patient_id FROM web_assessments WHERE assessment_id = %s",
                (assessment_id,),
            ).fetchone()
            self.assertEqual(str(wa_row[0]), p1["id"])

        # Executa revinculacao auditada para p2
        relink_resp = self.h.importer.post(
            f"/api/v1/projects/{self.h.project_id}/assessments/{assessment_id}/relink",
            json={
                "patient_id": p2["id"],
                "reason_code": "correcao_erro_humano_vinculo",
            },
        )
        self.assertEqual(relink_resp.status_code, 200, relink_resp.text)
        relink_data = relink_resp.json()
        self.assertEqual(relink_data["assessment_id"], assessment_id)
        self.assertEqual(relink_data["patient_id"], p2["id"])
        self.assertTrue(relink_data["relinked"])

        # Confere atualizacao das tabelas sem apagar avaliacao
        with psycopg.connect(self.database_url) as connection:
            wa_row = connection.execute(
                "SELECT patient_id FROM web_assessments WHERE assessment_id = %s",
                (assessment_id,),
            ).fetchone()
            self.assertEqual(str(wa_row[0]), p2["id"])

            a_row = connection.execute(
                "SELECT participant_id FROM assessments WHERE assessment_id = %s",
                (assessment_id,),
            ).fetchone()
            self.assertEqual(a_row[0], p2["participant_code"])

            inv_row = connection.execute(
                "SELECT patient_id, participant_id FROM web_invitations WHERE invitation_id = %s",
                (inv["invitation_id"],),
            ).fetchone()
            self.assertEqual(str(inv_row[0]), p2["id"])
            self.assertEqual(inv_row[1], p2["participant_code"])

            # Trilha de auditoria gerada para p1 e p2
            audit_events = connection.execute(
                """SELECT entity_id, action, reason_code FROM web_registry_audit_events
                   WHERE action = 'relink' AND entity_type = 'participant_link'
                   ORDER BY occurred_at ASC""",
            ).fetchall()
            self.assertGreaterEqual(len(audit_events), 2)
            entity_ids = {str(row[0]) for row in audit_events}
            self.assertIn(p1["id"], entity_ids)
            self.assertIn(p2["id"], entity_ids)

        # Ficha detalhada do p2 exibe a avaliacao e o evento de auditoria
        detail_p2 = self.h.consulta.get(f"/api/v1/patients/{p2['id']}").json()
        self.assertEqual(len(detail_p2["assessments"]), 1)
        self.assertEqual(detail_p2["assessments"][0]["assessment_id"], assessment_id)
        self.assertIn("relink", [ev["action"] for ev in detail_p2["audit_history"]])

        # Ficha detalhada do p1 nao tem mais a avaliacao, mas tem o registro auditado de relink
        detail_p1 = self.h.consulta.get(f"/api/v1/patients/{p1['id']}").json()
        self.assertEqual(len(detail_p1["assessments"]), 0)
        self.assertIn("relink", [ev["action"] for ev in detail_p1["audit_history"]])

        # Controles negativos
        self.assertEqual(
            self.h.consulta.post(
                f"/api/v1/projects/{self.h.project_id}/assessments/{assessment_id}/relink",
                json={"patient_id": p1["id"], "reason_code": "motivo"},
            ).status_code,
            403,
        )
        self.assertEqual(
            self.h.importer.post(
                f"/api/v1/projects/{self.h.project_id}/assessments/{assessment_id}/relink",
                json={"patient_id": p1["id"], "reason_code": ""},
            ).status_code,
            422,
        )

    def test_administrador_sem_vinculo_nao_acessa_cadastros_do_projeto(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "DELETE FROM web_project_members WHERE subject = %s",
                (helpers.ADMIN,),
            )
        created = self.h.admin.post(
            "/api/v1/patients",
            json={"full_name": "Paciente sintetico sem autorizacao"},
        )
        self.assertEqual(created.status_code, 403, created.text)
        listed = self.h.admin.get("/api/v1/patients")
        self.assertEqual(listed.status_code, 403, listed.text)


if __name__ == "__main__":
    unittest.main()
