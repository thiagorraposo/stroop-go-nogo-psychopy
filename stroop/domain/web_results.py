"""Validacao pura e normalizacao da conclusao do protocolo WEB aprovado."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math

from stroop.domain.stroop import calculate_metrics, expected_outcome


PROTOCOL_ID = "stroop_go_nogo_ptbr/0.2.2-web.1"
TEST_VERSION = "0.2.2-web.1"
TEST_CODE = "stroop_go_nogo_ptbr"
RESULT_FIELDS = frozenset({
    "protocol_id", "test_version", "platform", "app_version", "frame_period_ms", "trials",
})
TRIAL_FIELDS = frozenset({
    "trial_number", "condition_id", "key_pressed", "reaction_time_ms", "trial_start_ms",
    "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms", "key_at_ms",
})


class InvalidResultError(ValueError):
    """Corpo de conclusao inconsistente com o protocolo ou snapshot da sessao."""


def canonical_payload(payload: dict) -> bytes:
    """JSON UTF-8 ordenado, sem espacos e com numeros decimais normalizados.

    A forma decimal e explicita (sem expoente); 1/1.0 e -0/0 equivalem.
    A ordem das listas e preservada. Nao quantiza medidas antes do hash.
    """
    def encode(value):
        if value is None:
            return "null"
        if type(value) is bool:
            return "true" if value else "false"
        if type(value) is int:
            return str(value)
        if type(value) is float:
            if not math.isfinite(value):
                raise InvalidResultError("Numero nao finito.")
            if value == 0:
                return "0"
            decimal = format(Decimal(str(value)), "f")
            return decimal.rstrip("0").rstrip(".") if "." in decimal else decimal
        if type(value) is str:
            return json.dumps(value, ensure_ascii=False)
        if type(value) is list:
            return "[" + ",".join(encode(item) for item in value) + "]"
        if type(value) is dict and all(type(key) is str for key in value):
            return "{" + ",".join(
                encode(key) + ":" + encode(value[key]) for key in sorted(value)
            ) + "}"
        raise InvalidResultError("Tipo nao suportado no JSON canonico.")

    try:
        return encode(payload).encode("utf-8")
    except (UnicodeError, RecursionError, ValueError) as exc:
        raise InvalidResultError("Corpo nao pode ser canonizado.") from exc


def _number(value, field: str) -> Decimal:
    if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)):
        raise InvalidResultError(f"{field} deve ser numero finito.")
    return Decimal(str(value))


def _closed_object(value, fields: frozenset, name: str) -> None:
    if type(value) is not dict or set(value) != fields:
        raise InvalidResultError(f"Campos de {name} invalidos.")


def validate_result(payload: dict, order: tuple[int, ...], app_version: str,
                    conditions: list[dict]) -> dict:
    """Valida o registro original e deriva linhas/metricas sem confiar no cliente.

    ``conditions`` recebe as 16 linhas do snapshot principal, identificadas por
    ``condition_id``. As linhas normalizadas usam o contrato textual do nucleo,
    sem os metadados pessoais ou tecnicos de avaliacao, fornecidos pelo servidor.
    """
    _closed_object(payload, RESULT_FIELDS, "conclusao")
    for field, expected in (("protocol_id", PROTOCOL_ID), ("test_version", TEST_VERSION),
                            ("platform", "web"), ("app_version", app_version)):
        if type(payload[field]) is not str or payload[field] != expected:
            raise InvalidResultError(f"{field} incompativel com a sessao.")
    frame = _number(payload["frame_period_ms"], "frame_period_ms")
    if not Decimal(4) <= frame <= Decimal(50):
        raise InvalidResultError("Periodo de quadro fora do intervalo permitido.")
    if (len(order) != 16 or any(type(item) is not int for item in order)
            or set(order) != set(range(1, 17))):
        raise InvalidResultError("Ordem principal invalida.")
    sources = {row["condition_id"]: row for row in conditions}
    if len(conditions) != 16 or set(sources) != set(order):
        raise InvalidResultError("Snapshot de condicoes invalido.")
    trials = payload["trials"]
    if type(trials) is not list or len(trials) != 16:
        raise InvalidResultError("A conclusao exige 16 tentativas principais.")

    rows = []
    previous_end = Decimal(0)
    for index, trial in enumerate(trials, 1):
        _closed_object(trial, TRIAL_FIELDS, "tentativa")
        if type(trial["trial_number"]) is not int or trial["trial_number"] != index:
            raise InvalidResultError("Numeracao das tentativas invalida.")
        if (type(trial["condition_id"]) is not int
                or trial["condition_id"] != order[index - 1]):
            raise InvalidResultError("Condicao incompativel com a ordem da sessao.")
        start, onset, offset, end = (
            _number(trial[field], field) for field in (
                "trial_start_ms", "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms")
        )
        if not 0 <= start < onset < offset < end <= 60100 or start != previous_end:
            raise InvalidResultError("Tempos descontinuos ou fora dos limites.")
        if any(abs(actual - nominal) > frame for actual, nominal in (
            (start, Decimal((index - 1) * 3750)), (onset, start + 300),
            (offset, start + 2800), (end, start + 3750), (offset - onset, Decimal(2500)),
        )):
            raise InvalidResultError("Transicao excede a tolerancia de um quadro.")
        previous_end = end
        key = trial["key_pressed"]
        rt_value = trial["reaction_time_ms"]
        key_at_value = trial["key_at_ms"]
        if key is None:
            if rt_value is not None or key_at_value is not None:
                raise InvalidResultError("Ausencia de resposta exige tempos nulos.")
            reaction_time = ""
        else:
            if type(key) is not str or key != "space":
                raise InvalidResultError("Somente Espaco e uma resposta valida.")
            rt = _number(rt_value, "reaction_time_ms")
            key_at = _number(key_at_value, "key_at_ms")
            if not 0 < rt < 2500 or not onset < key_at < offset:
                raise InvalidResultError("Resposta fora da janela exclusiva.")
            if abs(key_at - onset - rt) > Decimal("0.001"):
                raise InvalidResultError("RT diverge do instante da resposta.")
            seconds = rt_value / 1000
            # O contrato interno usa DOUBLE; nunca substituir RT positivo por
            # zero por underflow nem fabricar um valor minimo metodologico.
            if not math.isfinite(seconds) or seconds <= 0:
                raise InvalidResultError("RT nao representavel em segundos.")
            reaction_time = str(seconds)
        source = sources[trial["condition_id"]]
        row = {
            "block": "main", "trial_number": str(index), "word": source["word"],
            "ink_color": source["ink_color"], "condition": source["condition"],
            "key_pressed": key or "", "reaction_time": reaction_time,
        }
        outcome = expected_outcome(row)
        if outcome is None:
            raise InvalidResultError("Condicao principal invalida.")
        row["correct_response"], row["correct"], row["error_type"] = outcome
        rows.append(row)
    if not Decimal(59900) <= previous_end <= Decimal(60100):
        raise InvalidResultError("Duracao principal excede a tolerancia de 100 ms.")

    metrics = calculate_metrics(rows)
    values = {metric["metric_code"]: metric["metric_value"] for metric in metrics}
    summary = {
        "accuracy": values["accuracy"],
        "response_time_seconds": values["response_time"] if values["hits"] else None,
        **{name: int(values[name]) for name in (
            "total_trials", "hits", "omission_errors", "commission_errors", "correct_rejections")},
    }
    return {"rows": rows, "metrics": metrics, "summary": summary,
            "payload_sha256": hashlib.sha256(canonical_payload(payload)).hexdigest()}
