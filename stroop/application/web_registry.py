"""Casos de uso dos cadastros centrais de pacientes e avaliadores (CHG-005)."""

from __future__ import annotations

from uuid import UUID

from stroop.domain.auth import AppUser
from stroop.domain.registry import (
    DuplicateCandidateError,
    InvalidRegistryDataError,
    normalize_person_name,
    normalize_search_term,
    validate_disambiguation_note,
    validate_initials,
    validate_reason_code,
    validate_search_query,
)
from stroop.persistence import web_registry as persistence
from stroop.persistence.web_registry import (
    EVALUATOR_SORTS,
    PATIENT_SORTS,
    ForbiddenRegistryError,
    MissingRegistryError,
    PersistenceError,
)


ACTIVE_FILTERS = frozenset({"true", "false", "all"})


def _pagination_params(page: object, page_size: object) -> tuple[int, int]:
    if type(page) is not int or not 1 <= page <= 100_000:
        raise InvalidRegistryDataError("Pagina invalida.")
    if type(page_size) is not int or not 1 <= page_size <= 100:
        raise InvalidRegistryDataError("Tamanho de pagina invalido.")
    return page, page_size


def find_duplicate_patients(
    database_url: str,
    actor: AppUser,
    *,
    full_name: str,
    initials: str | None = None,
) -> list[dict]:
    _, normalized_name = normalize_person_name(full_name)
    validated_initials = (
        validate_initials(initials) if initials is not None else None
    )
    return persistence.find_duplicate_patients(
        database_url,
        normalized_name=normalized_name,
        initials=validated_initials,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def create_patient(
    database_url: str,
    actor: AppUser,
    *,
    full_name: str,
    initials: str | None = None,
    disambiguation_note: str | None = None,
    confirm_homonym: bool = False,
) -> dict:
    if not isinstance(confirm_homonym, bool):
        raise InvalidRegistryDataError("Confirmacao de homonimo invalida.")
    cleaned_name, normalized_name = normalize_person_name(full_name)
    cleaned_initials = validate_initials(initials, fallback_name=cleaned_name)
    cleaned_note = validate_disambiguation_note(disambiguation_note)
    return persistence.create_patient(
        database_url,
        full_name=cleaned_name,
        normalized_name=normalized_name,
        initials=cleaned_initials,
        disambiguation_note=cleaned_note,
        confirm_homonym=confirm_homonym,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def list_patients(
    database_url: str,
    actor: AppUser,
    *,
    search: str | None = None,
    project_id: UUID | None = None,
    active: str = "all",
    page: int = 1,
    page_size: int = 25,
    sort: str = "name_asc",
) -> dict:
    if active not in ACTIVE_FILTERS:
        raise InvalidRegistryDataError("Filtro de atividade invalido.")
    if sort not in PATIENT_SORTS:
        raise InvalidRegistryDataError("Ordenacao de pacientes invalida.")
    page, page_size = _pagination_params(page, page_size)
    cleaned_search = validate_search_query(search)
    search_normalized = normalize_search_term(cleaned_search) if cleaned_search else ""
    return persistence.list_patients(
        database_url,
        search_normalized=search_normalized,
        search_raw=cleaned_search,
        project_id=project_id,
        active_filter=active,
        page=page,
        page_size=page_size,
        sort=sort,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def get_patient(database_url: str, actor: AppUser, patient_id: UUID) -> dict:
    return persistence.get_patient(
        database_url,
        patient_id=patient_id,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def update_patient(
    database_url: str,
    actor: AppUser,
    patient_id: UUID,
    *,
    full_name: str | None = None,
    initials: str | None = None,
    disambiguation_note: str | None = None,
    active: bool | None = None,
    reason_code: str,
) -> dict:
    if (
        full_name is None
        and initials is None
        and disambiguation_note is None
        and active is None
    ):
        raise InvalidRegistryDataError("Nenhum campo cadastral informado para atualizacao.")
    if active is not None and not isinstance(active, bool):
        raise InvalidRegistryDataError("Estado cadastral invalido.")
    cleaned_reason = validate_reason_code(reason_code)
    cleaned_name = None
    normalized_name = None
    if full_name is not None:
        cleaned_name, normalized_name = normalize_person_name(full_name)
    cleaned_initials = (
        validate_initials(initials) if initials is not None else None
    )
    cleaned_note = (
        validate_disambiguation_note(disambiguation_note)
        if disambiguation_note is not None
        else None
    )
    return persistence.update_patient(
        database_url,
        patient_id=patient_id,
        full_name=cleaned_name,
        normalized_name=normalized_name,
        initials=cleaned_initials,
        disambiguation_note=cleaned_note,
        active=active,
        reason_code=cleaned_reason,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def create_evaluator(
    database_url: str,
    actor: AppUser,
    *,
    full_name: str,
    initials: str | None = None,
    confirm_homonym: bool = False,
) -> dict:
    if not isinstance(confirm_homonym, bool):
        raise InvalidRegistryDataError("Confirmacao de homonimo invalida.")
    cleaned_name, normalized_name = normalize_person_name(full_name)
    cleaned_initials = validate_initials(initials, fallback_name=cleaned_name)
    return persistence.create_evaluator(
        database_url,
        full_name=cleaned_name,
        normalized_name=normalized_name,
        initials=cleaned_initials,
        confirm_homonym=confirm_homonym,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def list_evaluators(
    database_url: str,
    actor: AppUser,
    *,
    search: str | None = None,
    active: str = "all",
    page: int = 1,
    page_size: int = 25,
    sort: str = "name_asc",
) -> dict:
    if active not in ACTIVE_FILTERS:
        raise InvalidRegistryDataError("Filtro de atividade invalido.")
    if sort not in EVALUATOR_SORTS:
        raise InvalidRegistryDataError("Ordenacao de avaliadores invalida.")
    page, page_size = _pagination_params(page, page_size)
    cleaned_search = validate_search_query(search)
    search_normalized = normalize_search_term(cleaned_search) if cleaned_search else ""
    return persistence.list_evaluators(
        database_url,
        search_normalized=search_normalized,
        search_raw=cleaned_search,
        active_filter=active,
        page=page,
        page_size=page_size,
        sort=sort,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def get_evaluator(database_url: str, actor: AppUser, evaluator_id: UUID) -> dict:
    return persistence.get_evaluator(
        database_url,
        evaluator_id=evaluator_id,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def update_evaluator(
    database_url: str,
    actor: AppUser,
    evaluator_id: UUID,
    *,
    full_name: str | None = None,
    initials: str | None = None,
    active: bool | None = None,
    reason_code: str,
) -> dict:
    if full_name is None and initials is None and active is None:
        raise InvalidRegistryDataError("Nenhum campo cadastral informado para atualizacao.")
    if active is not None and not isinstance(active, bool):
        raise InvalidRegistryDataError("Estado cadastral invalido.")
    cleaned_reason = validate_reason_code(reason_code)
    cleaned_name = None
    normalized_name = None
    if full_name is not None:
        cleaned_name, normalized_name = normalize_person_name(full_name)
    cleaned_initials = (
        validate_initials(initials) if initials is not None else None
    )
    return persistence.update_evaluator(
        database_url,
        evaluator_id=evaluator_id,
        full_name=cleaned_name,
        normalized_name=normalized_name,
        initials=cleaned_initials,
        active=active,
        reason_code=cleaned_reason,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def relink_assessment(
    database_url: str,
    actor: AppUser,
    *,
    project_id: UUID,
    assessment_id: str,
    patient_id: UUID | None = None,
    evaluator_id: UUID | None = None,
    reason_code: str,
) -> dict:
    if patient_id is None and evaluator_id is None:
        raise InvalidRegistryDataError("Informe pelo menos um novo vinculo de paciente ou avaliador.")
    cleaned_reason = validate_reason_code(reason_code)
    return persistence.relink_assessment(
        database_url,
        project_id=project_id,
        assessment_id=assessment_id,
        patient_id=patient_id,
        evaluator_id=evaluator_id,
        reason_code=cleaned_reason,
        issuer=actor.issuer,
        subject=actor.subject,
    )


def relink_invitation(
    database_url: str,
    actor: AppUser,
    *,
    project_id: UUID,
    invitation_id: UUID,
    patient_id: UUID | None = None,
    evaluator_id: UUID | None = None,
    reason_code: str,
) -> dict:
    if patient_id is None and evaluator_id is None:
        raise InvalidRegistryDataError("Informe pelo menos um novo vinculo de paciente ou avaliador.")
    cleaned_reason = validate_reason_code(reason_code)
    return persistence.relink_invitation(
        database_url,
        project_id=project_id,
        invitation_id=invitation_id,
        patient_id=patient_id,
        evaluator_id=evaluator_id,
        reason_code=cleaned_reason,
        issuer=actor.issuer,
        subject=actor.subject,
    )


__all__ = [
    "DuplicateCandidateError",
    "ForbiddenRegistryError",
    "InvalidRegistryDataError",
    "MissingRegistryError",
    "PersistenceError",
    "create_evaluator",
    "create_patient",
    "find_duplicate_patients",
    "get_evaluator",
    "get_patient",
    "list_evaluators",
    "list_patients",
    "relink_assessment",
    "relink_invitation",
    "update_evaluator",
    "update_patient",
]
