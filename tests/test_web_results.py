"""Conclusoes sinteticas verificam classificacao, fronteiras e canonizacao WEB."""

from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import unittest

from stroop.domain.web_results import (
    InvalidResultError, PROTOCOL_ID, TEST_VERSION, canonical_payload, validate_result,
)


ROOT = Path(__file__).resolve().parents[1]
ORDER = (9, 1, 10, 2, 11, 3, 12, 4, 13, 5, 14, 6, 15, 7, 16, 8)
APP_VERSION = "web-0.1.0"


def synthetic_payload():
    return {
        "protocol_id": PROTOCOL_ID, "test_version": TEST_VERSION, "platform": "web",
        "app_version": APP_VERSION, "frame_period_ms": 16.666667,
        "trials": [{
            "trial_number": index + 1, "condition_id": condition,
            "key_pressed": None, "reaction_time_ms": None,
            "trial_start_ms": index * 3750, "stimulus_onset_ms": index * 3750 + 300,
            "stimulus_offset_ms": index * 3750 + 2800,
            "trial_end_ms": (index + 1) * 3750, "key_at_ms": None,
        } for index, condition in enumerate(ORDER)],
    }


def synthetic_conditions():
    with (ROOT / "condicoes/bloco_principal_stroop_go_nogo_ptbr.csv").open(
            encoding="utf-8", newline="") as source:
        return [{**row, "condition_id": int(row["trial_number"])}
                for row in csv.DictReader(source)]


def add_response(trial, rt=512):
    trial.update(key_pressed="space", reaction_time_ms=rt,
                 key_at_ms=trial["stimulus_onset_ms"] + rt)


class WebResultValidationTests(unittest.TestCase):
    def setUp(self):
        self.payload = synthetic_payload()
        self.conditions = synthetic_conditions()

    def validate(self, payload=None, **kwargs):
        return validate_result(self.payload if payload is None else payload,
                               kwargs.get("order", ORDER),
                               kwargs.get("app_version", APP_VERSION),
                               kwargs.get("conditions", self.conditions))

    def test_no_hits_preserves_legacy_sentinel_and_http_absence(self):
        result = self.validate()
        self.assertEqual(result["summary"], {
            "accuracy": 50, "response_time_seconds": None, "total_trials": 16,
            "hits": 0, "omission_errors": 8, "commission_errors": 0,
            "correct_rejections": 8,
        })
        self.assertEqual(next(m["metric_value"] for m in result["metrics"]
                              if m["metric_code"] == "response_time"), 0.0)
        self.assertTrue(all(row["reaction_time"] == "" for row in result["rows"]))
        self.assertTrue(all(set(row) == {
            "block", "trial_number", "word", "ink_color", "condition",
            "key_pressed", "reaction_time", "correct_response", "correct", "error_type",
        } for row in result["rows"]))

    def test_four_classifications_derive_from_sources_and_convert_seconds_once(self):
        add_response(self.payload["trials"][0], 681)
        add_response(self.payload["trials"][1], 512.123456789)
        add_response(self.payload["trials"][3], 731.123456789)
        original = deepcopy(self.payload)
        result = self.validate()
        self.assertEqual(self.payload, original)
        self.assertEqual([row["error_type"] for row in result["rows"][:4]],
                         ["commission", "hit", "correct_rejection", "hit"])
        self.assertEqual(result["rows"][4]["error_type"], "correct_rejection")
        self.assertEqual(result["rows"][5]["error_type"], "omission")
        self.assertEqual(result["rows"][0]["word"], "AZUL")
        self.assertEqual(result["rows"][0]["ink_color"], "gray")
        self.assertEqual(result["rows"][0]["correct"], "0")
        self.assertEqual(result["rows"][1]["correct_response"], "space")
        self.assertEqual(float(result["rows"][1]["reaction_time"]), 512.123456789 / 1000)
        self.assertAlmostEqual(result["summary"]["response_time_seconds"],
                               (512.123456789 / 1000 + 731.123456789 / 1000) / 2)
        self.assertEqual(result["summary"]["hits"], 2)

    def test_closed_top_level_schema(self):
        for field in self.payload:
            body = deepcopy(self.payload)
            del body[field]
            with self.subTest(missing=field), self.assertRaises(InvalidResultError):
                self.validate(body)
        for field in ("participant_name", "session_id", "assessment_id", "summary", "correct"):
            body = {**self.payload, field: "SINTETICO"}
            with self.subTest(extra=field), self.assertRaises(InvalidResultError):
                self.validate(body)
        for body in (None, [], "body", True):
            with self.subTest(type=type(body)), self.assertRaises(InvalidResultError):
                validate_result(body, ORDER, APP_VERSION, self.conditions)

    def test_closed_trial_schema(self):
        for field in self.payload["trials"][0]:
            body = deepcopy(self.payload)
            del body["trials"][0][field]
            with self.subTest(missing=field), self.assertRaises(InvalidResultError):
                self.validate(body)
        for field in ("correct", "word", "ink_color", "error_type", "block"):
            body = deepcopy(self.payload)
            body["trials"][0][field] = "synthetic"
            with self.subTest(extra=field), self.assertRaises(InvalidResultError):
                self.validate(body)
        self.payload["trials"][0] = None
        with self.assertRaises(InvalidResultError):
            self.validate()

    def test_versions_platform_are_exact_strings(self):
        for field in ("protocol_id", "test_version", "platform", "app_version"):
            for value in (None, True, 1, "wrong", self.payload[field] + " "):
                body = {**self.payload, field: value}
                with self.subTest(field=field, value=value), self.assertRaises(InvalidResultError):
                    self.validate(body)

    def test_trial_count_and_order(self):
        for trials in (None, {}, (), self.payload["trials"][:15],
                       self.payload["trials"] + [self.payload["trials"][0]],
                       list(reversed(self.payload["trials"]))):
            with self.subTest(trials=type(trials)), self.assertRaises(InvalidResultError):
                self.validate({**self.payload, "trials": trials})
        for field in ("trial_number", "condition_id"):
            for value in (True, 1.0, "1", 0, 17, 2):
                body = deepcopy(self.payload)
                body["trials"][0][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(InvalidResultError):
                    self.validate(body)
        with self.assertRaises(InvalidResultError):
            self.validate(order=ORDER[:-1] + (ORDER[0],))

    def test_frame_period_inclusive_and_strict_numeric_type(self):
        for frame in (4, 50, 4.0, 16.666667):
            with self.subTest(valid=frame):
                self.validate({**self.payload, "frame_period_ms": frame})
        for frame in (3.999999, 50.000001, True, "16", None, float("nan"), float("inf")):
            with self.subTest(invalid=frame), self.assertRaises(InvalidResultError):
                self.validate({**self.payload, "frame_period_ms": frame})

    def test_instants_reject_non_numeric_non_finite_negative_and_clock_reset(self):
        for field in ("trial_start_ms", "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms"):
            for value in (True, "300", None, float("nan"), float("inf"), -1, 60101):
                body = deepcopy(self.payload)
                body["trials"][0][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(InvalidResultError):
                    self.validate(body)
        for field, value in (("trial_start_ms", 0), ("stimulus_onset_ms", 0),
                             ("stimulus_offset_ms", 300), ("trial_end_ms", 2800)):
            body = deepcopy(self.payload)
            body["trials"][1 if field == "trial_start_ms" else 0][field] = value
            with self.subTest(field=field), self.assertRaises(InvalidResultError):
                self.validate(body)

    def test_first_start_zero_and_transitions_contiguous_without_tolerance(self):
        self.payload["trials"][0]["trial_start_ms"] = 0.000001
        with self.assertRaises(InvalidResultError):
            self.validate()
        self.payload = synthetic_payload()
        self.payload["trials"][1]["trial_start_ms"] += 0.000001
        with self.assertRaises(InvalidResultError):
            self.validate()

    def test_transition_and_stimulus_duration_gate_is_inclusive(self):
        self.payload["frame_period_ms"] = 4
        for field in ("stimulus_onset_ms", "stimulus_offset_ms"):
            for delta in (-4, 4):
                body = deepcopy(self.payload)
                body["trials"][0][field] += delta
                with self.subTest(field=field, valid_delta=delta):
                    self.validate(body)
            for delta in (-4.000001, 4.000001):
                body = deepcopy(self.payload)
                body["trials"][0][field] += delta
                with self.subTest(field=field, invalid_delta=delta), self.assertRaises(InvalidResultError):
                    self.validate(body)
        self.payload["trials"][0]["stimulus_onset_ms"] -= 4
        self.payload["trials"][0]["stimulus_offset_ms"] += 4
        with self.assertRaises(InvalidResultError):
            self.validate()  # Each transition passes; stimulus duration exceeds one frame.

    def test_nominal_start_end_gate_and_total_duration_inclusive(self):
        for direction in (-1, 1):
            body = synthetic_payload()
            body["frame_period_ms"] = 50
            body["trials"][0]["trial_end_ms"] += direction * 50
            for trial in body["trials"][1:]:
                for field in ("trial_start_ms", "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms"):
                    trial[field] += direction * 50
            body["trials"][-1]["trial_end_ms"] += direction * 50
            with self.subTest(valid_total=60000 + direction * 100):
                self.validate(body)
            body["trials"][-1]["trial_end_ms"] += direction * 0.001
            with self.subTest(invalid_total=direction), self.assertRaises(InvalidResultError):
                self.validate(body)
        # A continuous sequence cannot drift beyond a frame at a nominal start.
        body = synthetic_payload()
        body["frame_period_ms"] = 4
        body["trials"][0]["trial_end_ms"] += 4
        for trial in body["trials"][1:]:
            for field in ("trial_start_ms", "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms"):
                trial[field] += 4
        self.validate(body)
        body["trials"][1]["trial_end_ms"] += 0.001
        for trial in body["trials"][2:]:
            for field in ("trial_start_ms", "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms"):
                trial[field] += 0.001
        with self.assertRaises(InvalidResultError):
            self.validate(body)

    def test_response_presence_and_key_must_be_consistent(self):
        for changes in ({"reaction_time_ms": 10}, {"key_at_ms": 310},
                        {"key_pressed": "space"}, {"key_pressed": ""},
                        {"key_pressed": True}, {"key_pressed": "enter"}):
            body = deepcopy(self.payload)
            body["trials"][0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(InvalidResultError):
                self.validate(body)

    def test_response_open_bounds_and_rt_finite_strict_numeric(self):
        for rt in (0.000001, 2499.999999):
            body = deepcopy(self.payload)
            add_response(body["trials"][0], rt)
            with self.subTest(valid=rt):
                self.validate(body)
        for rt in (0, -1, 2500, 2501, True, "512", None, float("nan"), float("inf")):
            body = deepcopy(self.payload)
            add_response(body["trials"][0])
            body["trials"][0]["reaction_time_ms"] = rt
            with self.subTest(invalid=rt), self.assertRaises(InvalidResultError):
                self.validate(body)
        for key_at in (300, 2800, 299.999999, 2800.000001, True, "812", None,
                       float("nan"), float("inf")):
            body = deepcopy(self.payload)
            add_response(body["trials"][0])
            body["trials"][0]["key_at_ms"] = key_at
            with self.subTest(key_at=key_at), self.assertRaises(InvalidResultError):
                self.validate(body)

    def test_rt_tolerance_is_inclusive_and_never_relaxes_open_bounds(self):
        for delta in (-0.001, 0.001):
            body = deepcopy(self.payload)
            add_response(body["trials"][0])
            body["trials"][0]["reaction_time_ms"] += delta
            self.validate(body)
        for delta in (-0.001001, 0.001001):
            body = deepcopy(self.payload)
            add_response(body["trials"][0])
            body["trials"][0]["reaction_time_ms"] += delta
            with self.assertRaises(InvalidResultError):
                self.validate(body)
        for rt, key_at in ((0.0001, 300), (2499.9999, 2800)):
            body = deepcopy(self.payload)
            body["trials"][0].update(key_pressed="space", reaction_time_ms=rt, key_at_ms=key_at)
            with self.assertRaises(InvalidResultError):
                self.validate(body)

    def test_positive_rt_cannot_become_zero_when_normalized_to_double_seconds(self):
        trial = self.payload["trials"][0]
        trial.update(key_pressed="space", reaction_time_ms=5e-324,
                     key_at_ms=300.00000000000006)
        with self.assertRaises(InvalidResultError):
            self.validate()
        # A representable subnormal remains positive; no timing threshold is added.
        trial["reaction_time_ms"] = 5e-321
        result = self.validate()
        self.assertGreater(float(result["rows"][0]["reaction_time"]), 0)

    def test_hash_normalizes_representations_but_retains_actual_measurement(self):
        add_response(self.payload["trials"][0])
        first = self.validate()["payload_sha256"]
        equivalent = deepcopy(self.payload)
        equivalent["trials"][0]["reaction_time_ms"] = 512.0
        equivalent["trials"][0]["trial_start_ms"] = -0.0
        equivalent = dict(reversed(list(equivalent.items())))
        self.assertEqual(self.validate(equivalent)["payload_sha256"], first)
        equivalent["trials"][0]["reaction_time_ms"] += 0.00001
        self.assertNotEqual(self.validate(equivalent)["payload_sha256"], first)


class WebCanonicalPayloadTests(unittest.TestCase):
    def test_shared_vectors(self):
        vectors = json.loads((ROOT / "tests/fixtures/web_result_canonical.json").read_text(encoding="utf-8"))
        for vector in vectors:
            with self.subTest(vector=vector["name"]):
                actual = canonical_payload(vector["input"])
                self.assertEqual(actual.decode("utf-8"), vector["canonical"])
                self.assertEqual(hashlib.sha256(actual).hexdigest(), vector["sha256"])

    def test_list_order_changes_hash(self):
        self.assertNotEqual(canonical_payload({"a": [1, 2]}), canonical_payload({"a": [2, 1]}))

    def test_nonfinite_and_unsupported_types_are_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), (1,), {1: "key"}, b"x"):
            with self.subTest(value=value), self.assertRaises(InvalidResultError):
                canonical_payload({"value": value})


if __name__ == "__main__":
    unittest.main()
