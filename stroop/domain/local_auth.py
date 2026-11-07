"""Politicas puras da credencial local; senha preservada exatamente como recebida."""
from __future__ import annotations

import re
from hashlib import sha256
from stroop.domain.password_blocklist import COMMON_PASSWORD_SHA256

LOCAL_ISSUER = 'urn:stroop:local'
# Complemento local em portugues/exemplos; corpus publico derivado em
# password_blocklist.py. Nenhuma consulta externa com senha de usuario.
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
    if new and (value.casefold() in COMMON_PASSWORDS
                or sha256(value.casefold().encode("utf-8")).hexdigest() in COMMON_PASSWORD_SHA256
                or len(set(value)) == 1):
        raise InvalidCredential('Credencial invalida.')
    return value
