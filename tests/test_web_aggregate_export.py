"""Contrato sintético do CSV agregado; nenhuma coleta ou arquivo de participante."""
import csv
import io
import math
import unittest

from stroop.domain.web_aggregate_export import aggregate_filename, serialize_aggregate_csv

STROOP = "stroop_go_nogo_ptbr"
DEMO = "instrumento_sintetico_demo"


def synthetic_row(test_code=STROOP):
    return {
        "assessment_id": "AVALIACAO_SINTETICA", "project_id": "00000000-0000-4000-8000-000000000001",
        "project_code": "PROJETO_SINTETICO", "participant_id": "P_SINTETICO", "visit": "V1",
        "evaluator_id": "avaliador_sintetico", "started_at": "2026-10-17T10:00:00Z", "platform": "web",
        "test_code": test_code, "test_version": "1.0.0", "protocol_id": "sintetico", "app_version": "web-0.1.0",
        "summary": {"accuracy": 75.0, "accuracy_go_trials": 75.0, "accuracy_no_go_trials": 75.0,
                    "response_time_seconds": 0.5123456789012345, "total_trials": 16, "total_go_trials": 8,
                    "total_no_go_trials": 8, "hits": 6, "correct_rejections": 6, "omission_errors": 2,
                    "commission_errors": 2},
    }


def decoded(rows, code=STROOP):
    return list(csv.DictReader(io.StringIO(serialize_aggregate_csv(rows, test_code=code))))


class AggregateExportTests(unittest.TestCase):
    def test_stroop_fixed_units_and_parity_without_quantization(self):
        source = synthetic_row()
        result = decoded([source])[0]
        self.assertEqual(len(result), 23)
        for source_key, header in (("accuracy", "accuracy_percent"), ("accuracy_go_trials", "accuracy_go_trials_percent"),
                                   ("accuracy_no_go_trials", "accuracy_no_go_trials_percent"), ("response_time_seconds", "response_time_seconds")):
            self.assertEqual(float(result[header]), source["summary"][source_key])
        for key in ("total_trials", "total_go_trials", "total_no_go_trials", "hits", "correct_rejections", "omission_errors", "commission_errors"):
            self.assertEqual(int(result[f"{key}_count"]), source["summary"][key])
        self.assertEqual(result["project_code"], "PROJETO_SINTETICO")
        self.assertEqual(source["summary"]["response_time_seconds"], 0.5123456789012345)

    def test_whitelisted_metadata_excludes_identifiers_paths_and_extra_metrics(self):
        source = synthetic_row()
        source.update(participant_name="NOME_SINTETICO_PROIBIDO", initials="XX", source_file="CAMINHO_SINTETICO_PROIBIDO", session_id="SESSAO_INTERNA")
        source["summary"]["private_metric"] = 999
        text = serialize_aggregate_csv([source], test_code=STROOP)
        for forbidden in ("participant_name", "initials", "source_file", "session_id", "NOME_SINTETICO_PROIBIDO", "CAMINHO_SINTETICO_PROIBIDO", "private_metric", "999"):
            self.assertNotIn(forbidden, text)

    def test_standard_csv_unicode_delimiters_quotes_and_newlines(self):
        source = synthetic_row()
        source.update(project_code='SINTÉTICO, "α"; projeto', visit="V1\nSINTETICA", participant_id="P;SINTÉTICO")
        result = decoded([source])[0]
        self.assertEqual(result["project_code"], source["project_code"])
        self.assertEqual(result["visit"], source["visit"])
        self.assertEqual(result["participant_id"], source["participant_id"])
        text = serialize_aggregate_csv([source], test_code=STROOP)
        self.assertFalse(text.startswith("\ufeff"))
        self.assertIn("\r\n", text)
        self.assertEqual(text.encode("utf-8").decode("utf-8"), text)

    def test_formula_injection_is_escaped_even_after_whitespace(self):
        for malicious in ("=1+1", "+1+1", "-1+1", "@SUM(1)", "  =1+1", "\t+1+1", "\r@SUM(1)", "\n-1+1", "\tSINTETICO"):
            with self.subTest(value=repr(malicious)):
                source = synthetic_row(); source["participant_id"] = malicious
                self.assertEqual(decoded([source])[0]["participant_id"], "'" + malicious)

    def test_absence_empty_not_zero_and_legacy_civil_date_preserved(self):
        source = synthetic_row()
        source.update(evaluator_id=None, protocol_id=None, app_version=None, started_at="2026-10-17T10:00:00")
        source["summary"].update(accuracy_go_trials=None, response_time_seconds=None)
        result = decoded([source])[0]
        for key in ("evaluator_id", "protocol_id", "app_version", "accuracy_go_trials_percent", "response_time_seconds"):
            self.assertEqual(result[key], "")
        self.assertEqual(result["started_at"], "2026-10-17T10:00:00")

    def test_demo_units_negative_numbers_and_no_stroop_columns(self):
        source = synthetic_row(DEMO)
        source["summary"] = {"metrics": {"demo_total": -4, "demo_mean": -2.5123456789012345}}
        result = decoded([source], DEMO)[0]
        self.assertEqual(len(result), 14)
        self.assertEqual(result["demo_total_count"], "-4")
        self.assertEqual(result["demo_mean_unit"], str(source["summary"]["metrics"]["demo_mean"]))
        self.assertNotIn("accuracy_percent", result)
        self.assertNotIn("'", result["demo_total_count"])

    def test_empty_selection_has_header_and_static_safe_filename(self):
        for code, count in ((STROOP, 23), (DEMO, 14)):
            text = serialize_aggregate_csv([], test_code=code)
            self.assertEqual(len(list(csv.reader(io.StringIO(text)))[0]), count)
            self.assertEqual(list(csv.DictReader(io.StringIO(text))), [])
            self.assertEqual(aggregate_filename(code), f"{code}_avaliacoes.csv")
        for code in ("desconhecido", "../segredo", "=SINTETICO", None):
            with self.subTest(code=code), self.assertRaises(ValueError):
                aggregate_filename(code)
            with self.subTest(code=code), self.assertRaises(ValueError):
                serialize_aggregate_csv([], test_code=code)

    def test_nonfinite_bool_text_metrics_and_wrong_instrument_rejected(self):
        for invalid in (math.nan, math.inf, -math.inf, True, "=1+1", "0.5", []):
            with self.subTest(value=invalid):
                source = synthetic_row(); source["summary"]["accuracy"] = invalid
                with self.assertRaises(ValueError):
                    serialize_aggregate_csv([source], test_code=STROOP)
        for source in (synthetic_row(DEMO), {**synthetic_row(), "summary": None}, {**synthetic_row(), "project_code": 123}):
            with self.assertRaises(ValueError):
                serialize_aggregate_csv([source], test_code=STROOP)

    def test_one_row_per_assessment_including_repeated_visits(self):
        a, b = synthetic_row(), synthetic_row()
        b.update(assessment_id="OUTRA_AVALIACAO_SINTETICA", project_id="00000000-0000-4000-8000-000000000002")
        rows = decoded(iter([a, b]))
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["visit"] for row in rows], ["V1", "V1"])
        self.assertNotEqual(rows[0]["project_id"], rows[1]["project_id"])


if __name__ == "__main__":
    unittest.main()
