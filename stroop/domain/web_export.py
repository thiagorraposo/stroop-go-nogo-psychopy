"""Serializacao em memoria do CSV Stroop para exportacao WEB autorizada.

Nao autoriza acesso nem baixa arquivos. O adaptador profissional deve revalidar
escopo e fornecer metadados fixados no servidor, nunca enviados pelo participante.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import io
import math
import re
from uuid import UUID

from stroop.domain.errors import ImportValidationError
from stroop.domain.stroop import (
    ASSESSMENT_METADATA_COLUMNS, CANONICAL_COLUMNS, expected_outcome, validate_rows,
)
from stroop.domain.web_results import TEST_CODE, TEST_VERSION


def _civil(started_at: str, *, require_zone: bool = True) -> datetime:
    if not isinstance(started_at, str):
        raise ValueError("Horario de inicio invalido.")
    try:
        value = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        if require_zone and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError
        return value
    except (ValueError, OverflowError):
        raise ValueError("Horario de inicio invalido.") from None


def export_filename(started_at: str, *, allow_naive: bool = False) -> str:
    """Nome fixo sem identificadores, com instante civil em UTC."""
    value = _civil(started_at, require_zone=not allow_naive)
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc)
    return (f"{TEST_CODE}_{value.date().isoformat()}_"
            f"{value.hour:02}h{value.minute:02}m{value.second:02}s_trials.csv")


def _safe_cell(value: str) -> str:
    # Aspas CSV escapam delimitadores, mas nao impedem formulas de planilhas.
    if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value


def serialize_assessment_csv(metadata: dict, trials: list[dict]) -> str:
    """21 colunas, somente principal, RT ja em segundos e nomes mascarados.

    Recalcula classificacoes com o nucleo; preserva RT sem quantizacao, permitindo
    ao importador reproduzir as mesmas metricas da conclusao WEB. Nunca recebe
    milissegundos. Versoes locais conservam sua quantidade historica de linhas.
    """
    if metadata.get("test_code") != TEST_CODE or not trials:
        raise ValueError("Avaliacao incompativel com o CSV Stroop.")
    version = metadata.get("test_version")
    if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", version):
        raise ValueError("Versao invalida.")
    if version == TEST_VERSION and len(trials) != 16:
        raise ValueError("Avaliacao WEB incompleta.")
    assessment_id = metadata.get("assessment_id")
    if not isinstance(assessment_id, str) or not 1 <= len(assessment_id) <= 128:
        raise ValueError("Identificador de avaliacao invalido.")
    if version == TEST_VERSION:
        try:
            UUID(assessment_id)
        except (ValueError, AttributeError):
            raise ValueError("Identificador de avaliacao invalido.") from None
    started = _civil(metadata.get("started_at"), require_zone=version == TEST_VERSION)
    fixed = {column: metadata.get(column, "") for column in ASSESSMENT_METADATA_COLUMNS}
    fixed.update(participant_name="NAO_COLETADO", initials="")
    if version == TEST_VERSION:
        started = started.astimezone(timezone.utc)
        fixed.update(started_at=started.isoformat().replace("+00:00", "Z"),
                     assessment_date=started.date().isoformat())
    elif not fixed["assessment_date"]:
        fixed["assessment_date"] = started.date().isoformat()
    if any(not isinstance(value, str) for value in fixed.values()):
        raise ValueError("Metadados invalidos.")
    rows = []
    for index, source in enumerate(trials, 1):
        if source.get("block") != "main" or str(source.get("trial_number")) != str(index):
            raise ValueError("Tentativas incompletas ou fora de ordem.")
        row = {**fixed, "block": "main", "trial_number": str(index)}
        for key in ("word", "ink_color", "condition", "key_pressed"):
            value = source.get(key)
            row[key] = "" if value is None else value
            if not isinstance(row[key], str):
                raise ValueError("Tentativa invalida.")
        outcome = expected_outcome(row)
        if outcome is None:
            raise ValueError("Resposta invalida.")
        row["correct_response"], row["correct"], row["error_type"] = outcome
        raw_rt = source.get("reaction_time")
        if raw_rt is None or raw_rt == "":
            row["reaction_time"] = ""
        else:
            if isinstance(raw_rt, bool):
                raise ValueError("Tempo de resposta invalido.")
            try:
                seconds = float(raw_rt)
            except (ValueError, TypeError, OverflowError):
                raise ValueError("Tempo de resposta invalido.") from None
            if (not math.isfinite(seconds) or seconds <= 0
                    or (version == TEST_VERSION and seconds >= 2.5)):
                raise ValueError("Tempo de resposta invalido.")
            row["reaction_time"] = str(seconds)
        rows.append(row)
    if version == TEST_VERSION and sum(row['condition'] == 'congruent' for row in rows) != 8:
        raise ValueError("Balanceamento WEB invalido.")
    try:
        validate_rows(rows)
    except ImportValidationError:
        raise ValueError("Tentativas invalidas para exportacao.") from None
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CANONICAL_COLUMNS, extrasaction="raise")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _safe_cell(value) for key, value in row.items()})
    return output.getvalue()
