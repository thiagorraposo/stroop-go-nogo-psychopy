"""Registro de apresentacao dos instrumentos no dashboard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentView:
    code: str
    label: str
    metric_codes: tuple[str, ...]
    chart_metric_codes: tuple[str, ...]
    trial_detail: bool


INSTRUMENTS = {
    "stroop_go_nogo_ptbr": InstrumentView(
        code="stroop_go_nogo_ptbr",
        label="Stroop Go/No-Go",
        metric_codes=(
            "accuracy", "accuracy_go_trials", "accuracy_no_go_trials",
            "omission_errors", "commission_errors", "response_time",
        ),
        chart_metric_codes=("accuracy", "response_time"),
        trial_detail=True,
    ),
    "instrumento_sintetico_demo": InstrumentView(
        code="instrumento_sintetico_demo",
        label="Instrumento demonstrativo sintético",
        metric_codes=("demo_total", "demo_mean"),
        chart_metric_codes=("demo_total", "demo_mean"),
        trial_detail=False,
    ),
}


def instrument_view(code: str) -> InstrumentView:
    try:
        return INSTRUMENTS[code]
    except KeyError as exc:
        raise ValueError(f"Instrumento sem registro visual: {code}") from exc


def supported_codes() -> tuple[str, ...]:
    return tuple(INSTRUMENTS)
