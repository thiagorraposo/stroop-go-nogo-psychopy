"""Compatibilidade dos imports anteriores; implementacao em stroop.ingestion.

Novos consumidores devem importar diretamente o pacote stroop.
"""

from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stroop.ingestion.instruments import (
    InstrumentAdapter,
    InstrumentValidationError,
    NormalizedAssessment,
    SYNTHETIC_CODE,
    SYNTHETIC_COLUMNS,
    SYNTHETIC_METRICS,
    _build_adapters,
    _load_stroop,
    _load_synthetic,
    _read_rows,
    load_instrument_csv,
    supported_instruments,
)
