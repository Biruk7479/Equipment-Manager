import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.errors import UnauthorizedError

TokenType = Literal["access", "refresh"]

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int, session_id: uuid.UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return _encode(
        {"sub": str(user_id), "sid": str(session_id), "type": "access", "exp": expires_at}
    )


def create_refresh_token(user_id: int, token_id: uuid.UUID, expires_at: datetime) -> str:
    return _encode(
        {"sub": str(user_id), "type": "refresh", "jti": str(token_id), "exp": expires_at}
    )


def decode_token(token: str, token_type: TokenType) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
    if payload.get("type") != token_type:
        raise UnauthorizedError("Invalid or expired token")
    return payload


def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
