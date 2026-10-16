"""Erros publicos dos casos de uso de importacao PostgreSQL."""


class PostgresImportError(Exception):
    """Falha publica sem dados de entrada ou detalhes de conexao."""


class DuplicateAssessmentError(PostgresImportError):
    """Avaliacao existente; substituicao exige --force."""
