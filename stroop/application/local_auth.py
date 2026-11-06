"""Casos de uso locais; politicas, criptografia e persistencia separadas da UI."""
from __future__ import annotations

from stroop.domain.auth import PERMISSIONS
from stroop.domain.local_auth import normalize_username, validate_password
from stroop.persistence import local_auth as persistence
from stroop.security.passwords import hash_password, verify_password, needs_rehash


def provision(database_url: str, username: str, password: str, *, recover: bool = False) -> bool:
    username = normalize_username(username)
    return persistence.provision(database_url, username, hash_password(password), recover=recover)


def authenticate(database_url, username, password, bucket, token_hash, previous_hash=None):
    username = normalize_username(username)
    validate_password(password, new=False)
    return persistence.authenticate(database_url, username, password, bucket, token_hash,
                                    previous_hash, verify_password, hash_password, needs_rehash)


def change_password(database_url, token_hash, current_password, new_password):
    validate_password(current_password, new=False)
    return persistence.change_password(database_url, token_hash, current_password,
                                       hash_password(new_password), verify_password)


def session_context(database_url, token_hash, action):
    if action not in PERMISSIONS:
        raise ValueError('Operacao protegida desconhecida.')
    return persistence.session_context(database_url, token_hash, PERMISSIONS[action])
