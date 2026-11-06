"""Casos de uso locais; politicas, criptografia e persistencia separadas da UI."""
from __future__ import annotations

from stroop.domain.auth import PERMISSIONS
from stroop.domain.local_auth import normalize_username, validate_password
from stroop.persistence import local_auth as persistence
from stroop.security.passwords import hash_password, verify_password, needs_rehash


def provision(database_url: str, username: str, password: str, *, recover: bool = False) -> bool:
    username = normalize_username(username)
    return persistence.provision(database_url, username, hash_password(password), recover=recover)


def authenticate(database_url, username, password, bucket, token_hash, previous_hash=None,
                 *, origin_bucket=None, origin_limit=20, origin_window_seconds=60):
    username = normalize_username(username)
    validate_password(password, new=False)
    return persistence.authenticate(database_url, username, password, bucket, token_hash,
                                    previous_hash, verify_password, lambda value: hash_password(value, new=False), needs_rehash,
                                    origin_bucket=origin_bucket, origin_limit=origin_limit,
                                    origin_window_seconds=origin_window_seconds)


def change_password(database_url, token_hash, current_password, new_password):
    validate_password(current_password, new=False)
    validate_password(new_password)
    return persistence.change_password(database_url, token_hash, current_password,
                                       new_password, verify_password, hash_password)[0] == 'success'


def change_password_limited(database_url, token_hash, current_password, new_password, *,
                            bucket_for_username, origin_bucket=None, origin_limit=20,
                            origin_window_seconds=60):
    """Compartilha limite do identificador com login; hash novo somente apos senha atual."""
    validate_password(current_password, new=False)
    validate_password(new_password)
    return persistence.change_password(database_url, token_hash, current_password,
                                       new_password, verify_password, hash_password,
                                       bucket_for_username=bucket_for_username,
                                       origin_bucket=origin_bucket, origin_limit=origin_limit,
                                       origin_window_seconds=origin_window_seconds)


def session_context(database_url, token_hash, action):
    if action not in PERMISSIONS:
        raise ValueError('Operacao protegida desconhecida.')
    return persistence.session_context(database_url, token_hash, PERMISSIONS[action])
