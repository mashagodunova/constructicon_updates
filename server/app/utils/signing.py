from typing import Any
import datetime

import jose.exceptions
from jose import jwt

from app.core import settings

__all__ = ('sign', 'unsign', 'Signer',)


Expires = datetime.datetime | datetime.timedelta | int

class VerificationError(jose.exceptions.JWTError):
    pass

class Signer:
    def __init__(
            self, key: str | None = None, salt: str | None = None,
            algorithm: str | None=None, fallback_keys: list[str] | None = None,
            expires: Expires | None = None,
        ) -> None:
        self.key = key or settings.SECRET_KEY or 'key'
        if salt:
            self.key += salt or 'salt'

        if fallback_keys is None:
            fallback_keys = getattr(settings, 'SECRET_KEY_FALLBACKS', [])
        self.algorithm = algorithm or 'HS256'
        self.keys = [self.key, *fallback_keys]
        self.expires = getattr(settings, 'SIGNING_DEFAULT_EXPIRES', None)

    def sign(self, payload: Any, expires: Expires | None = None) -> str:
        expires = expires if expires else self.expires

        if expires is not None:
            if isinstance(expires, int):
                expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
            elif isinstance(expires, datetime.timedelta):
                expires = datetime.datetime.utcnow() + expires

        data = {'p': payload}
        if expires:
            data['exp'] = expires

        return jwt.encode(data, self.key, algorithm=self.algorithm)

    def unsign(self, data: str) -> Any:
        for key in self.keys:
            try:
                return jwt.decode(data, key, algorithms=[self.algorithm])['p']
            except jose.exceptions.JWTError:
                continue

        raise VerificationError('Signature verification failed.')


def sign(payload: Any, expires: Expires | None = None, salt: str | None = None) -> str:
    return Signer(salt=salt).sign(payload, expires=expires)


def unsign(data: str, salt: str | None = None) -> Any:
    return Signer(salt=salt).unsign(data)
