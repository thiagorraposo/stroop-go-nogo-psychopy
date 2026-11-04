"""Contrato normalizado existente de avaliacao."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedAssessment:
    """Resultado comum consumido pelos importadores SQLite e PostgreSQL."""

    adapter_code: str
    metadata: dict[str, str]
    metrics: list[dict[str, Any]]
    trial_values: list[tuple[Any, ...]]
