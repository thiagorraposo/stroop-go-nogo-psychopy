"""Politicas puras da credencial local; senha preservada exatamente como recebida."""
from __future__ import annotations

import re

LOCAL_ISSUER = 'urn:stroop:local'
# Lista local minima de senhas comuns; nao e consulta externa nem prova de
# inexistencia em vazamentos. Revisao operacional pode ampliar a lista.
COMMON_PASSWORDS = frozenset({
    'passwordpassword', 'password123456789', '123456789012345',
    '1234567890123456', '12345678901234567890', 'qwertyuiopasdfgh',
    'qwertyuiop123456', 'correct horse battery staple',
    'senha123456789012', 'administrador123', 'administrator123',
    'letmeinletmeinletmein', 'iloveyouiloveyou',
})


class InvalidCredential(ValueError):
    """Credencial fora da politica, sem refletir seu conteudo."""


def normalize_username(value: str) -> str:
    if not isinstance(value, str):
        raise InvalidCredential('Credencial invalida.')
    value = value.strip()
    if not value.isascii():
        raise InvalidCredential('Credencial invalida.')
    value = value.lower()
    if re.fullmatch(r'[a-z0-9_.-]{1,64}', value, flags=re.ASCII) is None:
        raise InvalidCredential('Credencial invalida.')
    return value


def validate_password(value: str, *, new: bool = True) -> str:
    if (not isinstance(value, str) or not 15 <= len(value) <= 128
            or any(0xD800 <= ord(character) <= 0xDFFF for character in value)):
        raise InvalidCredential('Credencial invalida.')
    if new and (value.casefold() in COMMON_PASSWORDS or len(set(value)) == 1):
        raise InvalidCredential('Credencial invalida.')
    return value
