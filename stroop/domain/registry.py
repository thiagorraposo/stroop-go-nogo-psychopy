"""Regras puras de validacao, normalizacao e codigos de pacientes e avaliadores."""

from __future__ import annotations

from datetime import date
import re
import unicodedata


PATIENT_CODE_PATTERN = re.compile(r"^PAT-[0-9]{8}-[0-9]{6,}$")
EVALUATOR_CODE_PATTERN = re.compile(r"^EVA-[0-9]{6,}$")
STOPWORDS = frozenset({"da", "de", "do", "das", "dos", "e"})

PREPARATION_INSTRUMENTS: dict[str, dict[str, str]] = {
    "stroop_go_nogo_ptbr": {
        "test_code": "stroop_go_nogo_ptbr",
        "test_version": "0.2.2-web.1",
        "protocol_id": "stroop_go_nogo_ptbr/0.2.2-web.1",
        "name": "Stroop Go/No-Go (PT-BR)",
    },
}


class InvalidRegistryDataError(ValueError):
    """Entrada cadastral fora do contrato de dominio."""


class DuplicateCandidateError(Exception):
    """Cadastro com nome normalizado coincidente exige confirmacao explicita."""

    def __init__(self, candidates: list[dict[str, object]]) -> None:
        super().__init__("Possivel duplicidade ou homonimo detectado.")
        self.candidates = candidates


def _has_control_chars(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


def _strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def normalize_person_name(value: object) -> tuple[str, str]:
    """Valida full_name (2..120 chars) e produz normalized_name sem acentos."""
    if not isinstance(value, str) or _has_control_chars(value):
        raise InvalidRegistryDataError("Nome completo invalido.")
    cleaned = " ".join(value.strip().split())
    if not 2 <= len(cleaned) <= 120:
        raise InvalidRegistryDataError("Nome completo deve ter entre 2 e 120 caracteres.")
    normalized = " ".join(_strip_accents(cleaned).casefold().split())
    if not 2 <= len(normalized) <= 120:
        raise InvalidRegistryDataError("Nome normalizado invalido.")
    return cleaned, normalized


def derive_initials(full_name: str) -> str:
    """Deriva iniciais legiveis (ate 16 caracteres) a partir do nome completo."""
    _, normalized = normalize_person_name(full_name)
    tokens = [token for token in normalized.split(" ") if token]
    filtered = [token for token in tokens if token not in STOPWORDS] or tokens
    letters = [token[0].upper() for token in filtered if token[0].isalnum()]
    return "".join(letters)[:16]


def validate_initials(
    value: object,
    *,
    fallback_name: str | None = None,
) -> str:
    """Valida iniciais (0..16 chars) ou deriva automaticamente quando omitidas."""
    if value is None:
        return derive_initials(fallback_name) if fallback_name else ""
    if not isinstance(value, str) or _has_control_chars(value):
        raise InvalidRegistryDataError("Iniciais invalidas.")
    cleaned = " ".join(value.strip().split())
    if len(cleaned) > 16:
        raise InvalidRegistryDataError("Iniciais devem ter no maximo 16 caracteres.")
    return cleaned


def validate_disambiguation_note(value: object) -> str:
    """Valida nota curta opcional de desambiguacao (0..160 chars)."""
    if value is None:
        return ""
    if not isinstance(value, str) or _has_control_chars(value):
        raise InvalidRegistryDataError("Observacao de desambiguacao invalida.")
    cleaned = " ".join(value.strip().split())
    if len(cleaned) > 160:
        raise InvalidRegistryDataError(
            "Observacao de desambiguacao deve ter no maximo 160 caracteres."
        )
    return cleaned


def validate_reason_code(value: object) -> str:
    """Valida motivo auditavel de alteracao cadastral (1..120 chars)."""
    if not isinstance(value, str) or _has_control_chars(value):
        raise InvalidRegistryDataError("Motivo de alteracao invalido.")
    cleaned = " ".join(value.strip().split())
    if not 1 <= len(cleaned) <= 120:
        raise InvalidRegistryDataError(
            "Motivo de alteracao deve ter entre 1 e 120 caracteres."
        )
    return cleaned


def validate_search_query(value: object) -> str:
    """Normaliza termo de pesquisa textual (0..120 chars)."""
    if value is None:
        return ""
    if not isinstance(value, str) or _has_control_chars(value):
        raise InvalidRegistryDataError("Filtro de busca invalido.")
    cleaned = " ".join(value.strip().split())
    if len(cleaned) > 120:
        raise InvalidRegistryDataError("Filtro de busca excede 120 caracteres.")
    return cleaned


def normalize_search_term(value: str) -> str:
    """Converte termo de busca para forma sem acentos e em minusculas."""
    return " ".join(_strip_accents(value).casefold().split())


def format_patient_code(day: date, sequence_value: int) -> str:
    """Formata codigo estavel de paciente PAT-YYYYMMDD-NNNNNN."""
    if not isinstance(day, date) or type(sequence_value) is not int or sequence_value < 1:
        raise InvalidRegistryDataError("Parametros de codigo de paciente invalidos.")
    code = f"PAT-{day.strftime('%Y%m%d')}-{sequence_value:06d}"
    if PATIENT_CODE_PATTERN.fullmatch(code) is None or len(code) > 64:
        raise InvalidRegistryDataError("Codigo de paciente gerado fora do padrao.")
    return code


def format_evaluator_code(sequence_value: int) -> str:
    """Formata codigo estavel de avaliador EVA-NNNNNN."""
    if type(sequence_value) is not int or sequence_value < 1:
        raise InvalidRegistryDataError("Sequencia de codigo de avaliador invalida.")
    code = f"EVA-{sequence_value:06d}"
    if EVALUATOR_CODE_PATTERN.fullmatch(code) is None or len(code) > 64:
        raise InvalidRegistryDataError("Codigo de avaliador gerado fora do padrao.")
    return code


def validate_test_code(value: object) -> dict[str, str]:
    """Valida codigo de instrumento registrado para preparacao de sessao."""
    if value is None:
        return dict(PREPARATION_INSTRUMENTS["stroop_go_nogo_ptbr"])
    if not isinstance(value, str) or _has_control_chars(value):
        raise InvalidRegistryDataError("Codigo de instrumento invalido.")
    cleaned = value.strip()
    instrument = PREPARATION_INSTRUMENTS.get(cleaned)
    if instrument is None:
        raise InvalidRegistryDataError("Instrumento nao registrado para preparacao.")
    return dict(instrument)


__all__ = [
    "DuplicateCandidateError",
    "EVALUATOR_CODE_PATTERN",
    "InvalidRegistryDataError",
    "PATIENT_CODE_PATTERN",
    "PREPARATION_INSTRUMENTS",
    "derive_initials",
    "format_evaluator_code",
    "format_patient_code",
    "normalize_person_name",
    "normalize_search_term",
    "validate_disambiguation_note",
    "validate_initials",
    "validate_reason_code",
    "validate_search_query",
    "validate_test_code",
]
