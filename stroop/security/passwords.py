"""Argon2id pela API mantida de argon2-cffi; sem criptografia propria."""
from __future__ import annotations

import secrets
from threading import BoundedSemaphore

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

from stroop.domain.local_auth import validate_password

# Acima do piso documentado (19 MiB/t=2/p=1); limites independentes no banco
# e no proxy tambem sao necessarios em processos distintos.
HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=1, type=Type.ID)
VERIFY_SLOTS = BoundedSemaphore(2)
DUMMY_HASH = HASHER.hash(secrets.token_urlsafe(48))


class PasswordServiceUnavailable(RuntimeError):
    """Custo concorrente ou material codificado indisponivel."""


def hash_password(password: str) -> str:
    validate_password(password)
    return HASHER.hash(password)


def verify_password(encoded: str | None, password: str) -> bool:
    validate_password(password, new=False)
    if not VERIFY_SLOTS.acquire(blocking=False):
        raise PasswordServiceUnavailable('Verificacao indisponivel.')
    try:
        try:
            return HASHER.verify(encoded or DUMMY_HASH, password)
        except InvalidHashError:
            raise PasswordServiceUnavailable('Verificacao indisponivel.') from None
        except VerificationError:
            return False
    finally:
        VERIFY_SLOTS.release()


def needs_rehash(encoded: str) -> bool:
    return HASHER.check_needs_rehash(encoded)
