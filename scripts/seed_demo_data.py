#!/usr/bin/env python3
"""Popula o banco local com pacientes, avaliadores e avaliações sintéticas realistas."""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import sys
from uuid import uuid4
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg
from stroop.domain.local_auth import LOCAL_ISSUER
from stroop.domain.registry import format_patient_code, format_evaluator_code, normalize_person_name

DEFAULT_DB_URL = "postgresql://synthetic:synthetic-ci-only@127.0.0.1:32769/stroop_etapa4_test_ci"

PATIENTS = [
    ("Ana Carolina Sintética", "ACS"),
    ("Carlos Eduardo Sintético", "CES"),
    ("Mariana Souza Sintética", "MSS"),
    ("Roberto Lima Sintético", "RLS"),
    ("Fernanda Alves Sintética", "FAS"),
]

EVALUATORS = [
    ("Dra. Beatriz Sintética", "BS"),
    ("Dr. Marcelo Sintético", "MS"),
]

WORDS = ["VERMELHO", "VERDE", "AZUL", "AMARELO"]
COLORS = ["vermelho", "verde", "azul", "amarelo"]

METRIC_LABELS = {
    "total_trials": "Total de tentativas",
    "hits": "Acertos (Go)",
    "omission_errors": "Erros de omissão (Go sem resposta)",
    "commission_errors": "Erros de comissão (No-Go com resposta)",
    "correct_rejections": "Rejeições corretas (No-Go)",
    "accuracy": "Acurácia geral (%)",
    "accuracy_go_trials": "Acurácia Go (%)",
    "accuracy_no_go_trials": "Acurácia No-Go (%)",
    "total_go_trials": "Total de tentativas Go",
    "total_no_go_trials": "Total de tentativas No-Go",
    "mean_reaction_time_congruent": "Tempo de reação médio congruente (ms)",
    "mean_reaction_time_incongruent": "Tempo de reação médio incongruente (ms)",
    "median_reaction_time": "Tempo de reação mediano (ms)",
    "stroop_effect_reaction_time": "Efeito Stroop de tempo (ms)",
    "stroop_effect_accuracy": "Efeito Stroop de acurácia (%)",
    "response_time": "Tempo médio de resposta (ms)",
}

def seed():
    database = os.environ.get("TEST_DATABASE_URL", DEFAULT_DB_URL)
    with psycopg.connect(database, autocommit=True) as conn:
        print("Populando cadastros centrais de pacientes e avaliadores...")
        admin_row = conn.execute("SELECT principal_id FROM web_local_credentials WHERE username='admin'").fetchone()
        admin_subject = str(admin_row[0]) if admin_row else 'admin'

        # Garantir projeto padrão
        proj_row = conn.execute("SELECT project_id FROM web_projects WHERE code='PROJ_STROOP'").fetchone()
        if not proj_row:
            proj_id = uuid4()
            conn.execute("INSERT INTO web_projects (project_id, code, name, active, created_by_issuer, created_by_subject) VALUES (%s, %s, %s, TRUE, %s, %s)",
                         (proj_id, 'PROJ_STROOP', 'Pesquisa Stroop Go/No-Go', LOCAL_ISSUER, admin_subject))
        else:
            proj_id = proj_row[0]

        # Garantir que admin seja membro de todos os projetos ativos
        conn.execute("""
            INSERT INTO web_project_members (project_id, issuer, subject, active)
            SELECT project_id, %s, %s, TRUE
            FROM web_projects
            ON CONFLICT (project_id, issuer, subject) DO UPDATE SET active=TRUE
        """, (LOCAL_ISSUER, admin_subject))

        projects = conn.execute("SELECT project_id, code FROM web_projects WHERE active=TRUE").fetchall()

        # Vincular projetos a web_legacy_project_links para que as avaliações apareçam em todos eles
        for p_id, p_code in projects:
            conn.execute("""
                INSERT INTO web_legacy_project_links (project_id, legacy_project, active, created_at)
                VALUES (%s, %s, TRUE, NOW())
                ON CONFLICT DO NOTHING
            """, (p_id, p_code))
            conn.execute("""
                INSERT INTO web_legacy_project_links (project_id, legacy_project, active, created_at)
                VALUES (%s, 'PROJ_STROOP', TRUE, NOW())
                ON CONFLICT DO NOTHING
            """, (p_id,))

        today = datetime.now(timezone.utc).date()
        
        # Pacientes
        for idx, (name, inits) in enumerate(PATIENTS, 1):
            cleaned, normalized = normalize_person_name(name)
            p_code = format_patient_code(today, idx)
            conn.execute("""
                INSERT INTO web_patients (id, participant_code, full_name, normalized_name, initials, created_by_issuer, created_by_subject)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (participant_code) DO NOTHING
            """, (uuid4(), p_code, cleaned, normalized, inits, LOCAL_ISSUER, admin_subject))

        # Avaliadores
        for idx, (name, inits) in enumerate(EVALUATORS, 1):
            cleaned, normalized = normalize_person_name(name)
            e_code = format_evaluator_code(idx)
            conn.execute("""
                INSERT INTO web_evaluators (id, evaluator_code, full_name, normalized_name, initials, created_by_issuer, created_by_subject)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (evaluator_code) DO NOTHING
            """, (uuid4(), e_code, cleaned, normalized, inits, LOCAL_ISSUER, admin_subject))

        patient_records = conn.execute("SELECT id, participant_code, full_name, initials FROM web_patients").fetchall()
        evaluator_records = conn.execute("SELECT id, evaluator_code, full_name, initials FROM web_evaluators").fetchall()

        # Limpar dados prévios sintéticos
        conn.execute("DELETE FROM trial_results WHERE assessment_id LIKE 'ASS-STROOP-%'")
        conn.execute("DELETE FROM assessment_metrics WHERE assessment_id LIKE 'ASS-STROOP-%'")
        conn.execute("DELETE FROM assessments WHERE assessment_id LIKE 'ASS-STROOP-%'")

        now = datetime.now(timezone.utc)
        print("Gerando avaliações sintéticas completas (com trials e métricas)...")

        total_created = 0
        for idx, p in enumerate(patient_records):
            p_uuid, p_code, p_name, p_inits = p
            for v_idx, visit in enumerate(["V1", "V2"]):
                ass_id = f"ASS-STROOP-{p_code}-{visit}"
                eva = evaluator_records[idx % len(evaluator_records)]
                e_uuid, e_code, e_name, e_inits = eva

                days_ago = (len(patient_records) - idx) * 3 + (1 if visit == "V1" else 0)
                started_at = now - timedelta(days=days_ago, hours=random.randint(1, 8), minutes=random.randint(0, 59))
                ass_date = started_at.date()

                conn.execute("""
                    INSERT INTO assessments (
                        assessment_id, test_code, test_version, project, participant_id,
                        participant_name, initials, visit, evaluator, assessment_date,
                        started_at, source_file, imported_at, import_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ass_id, 'stroop_go_nogo_ptbr', '0.2.2-web.1', 'PROJ_STROOP', p_code,
                    p_name, p_inits, visit, e_name, ass_date, started_at, 'web-native', now, 'valid'
                ))

                # Gerar 16 trials (8 congruentes, 8 incongruentes)
                hits = 0
                correct_rejections = 0
                omissions = 0
                commissions = 0
                congruent_rts = []
                incongruent_rts = []

                for trial_num in range(1, 17):
                    is_congruent = (trial_num % 2 == 1)
                    word = random.choice(WORDS)
                    if is_congruent:
                        color = word.lower()
                        condition = "congruent"
                        correct_resp = "space"
                        if random.random() < 0.90:
                            key_pressed = "space"
                            correct = 1
                            error_type = "hit"
                            rt = round(random.uniform(0.38, 0.52), 4)
                            hits += 1
                            congruent_rts.append(rt)
                        else:
                            key_pressed = None
                            correct = 0
                            error_type = "omission"
                            rt = None
                            omissions += 1
                    else:
                        other_colors = [c for c in COLORS if c != word.lower()]
                        color = random.choice(other_colors)
                        condition = "incongruent"
                        correct_resp = None
                        if random.random() < 0.85:
                            key_pressed = None
                            correct = 1
                            error_type = "correct_rejection"
                            rt = None
                            correct_rejections += 1
                        else:
                            key_pressed = "space"
                            correct = 0
                            error_type = "commission"
                            rt = round(random.uniform(0.35, 0.48), 4)
                            commissions += 1
                            incongruent_rts.append(rt)

                    conn.execute("""
                        INSERT INTO trial_results (
                            assessment_id, block, trial_number, word, ink_color,
                            condition, correct_response, key_pressed, reaction_time,
                            correct, error_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        ass_id, 'main', trial_num, word, color, condition,
                        correct_resp, key_pressed, rt, correct, error_type
                    ))

                # Calcular métricas
                total_trials = 16
                accuracy = round(((hits + correct_rejections) / total_trials) * 100, 2)
                accuracy_go = round((hits / 8) * 100, 2)
                accuracy_no_go = round((correct_rejections / 8) * 100, 2)
                mean_rt_cong = round(sum(congruent_rts) / len(congruent_rts) * 1000, 2) if congruent_rts else 450.0
                mean_rt_incong = round(sum(incongruent_rts) / len(incongruent_rts) * 1000, 2) if incongruent_rts else 520.0
                all_rts = congruent_rts + incongruent_rts
                mean_rt_all = round(sum(all_rts) / len(all_rts) * 1000, 2) if all_rts else 460.0
                median_rt = mean_rt_all
                stroop_effect_rt = round(mean_rt_incong - mean_rt_cong, 2)
                stroop_effect_acc = round(accuracy * 0.15, 2)

                metric_values = {
                    "total_trials": (total_trials, "tentativas"),
                    "hits": (hits, "tentativas"),
                    "omission_errors": (omissions, "erros"),
                    "commission_errors": (commissions, "erros"),
                    "correct_rejections": (correct_rejections, "tentativas"),
                    "accuracy": (accuracy, "%"),
                    "accuracy_go_trials": (accuracy_go, "%"),
                    "accuracy_no_go_trials": (accuracy_no_go, "%"),
                    "total_go_trials": (8, "tentativas"),
                    "total_no_go_trials": (8, "tentativas"),
                    "mean_reaction_time_congruent": (mean_rt_cong, "ms"),
                    "mean_reaction_time_incongruent": (mean_rt_incong, "ms"),
                    "median_reaction_time": (median_rt, "ms"),
                    "stroop_effect_reaction_time": (stroop_effect_rt, "ms"),
                    "stroop_effect_accuracy": (stroop_effect_acc, "%"),
                    "response_time": (mean_rt_all, "ms"),
                }

                for m_code, (m_val, m_unit) in metric_values.items():
                    conn.execute("""
                        INSERT INTO assessment_metrics (
                            assessment_id, metric_code, metric_label, metric_value, unit, calculated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (ass_id, m_code, METRIC_LABELS[m_code], m_val, m_unit, now))

                total_created += 1

        print(f"Base populada com sucesso! {total_created} avaliações sintéticas completas geradas.")

if __name__ == "__main__":
    seed()
