"""Excecoes de validacao existentes, compartilhadas pelos adaptadores."""

class InstrumentValidationError(Exception):
    """Entrada ausente, malformada ou incompatível com um instrumento."""


class ImportValidationError(Exception):
    """Erro de validacao do CSV ou da importacao."""
