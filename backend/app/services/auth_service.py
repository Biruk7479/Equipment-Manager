import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError, TooManyRequestsError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import RefreshToken, User
from app.repositories import login_failure_repository, refresh_token_repository, user_repository
from app.schemas.auth import ChangePasswordIn


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


def authenticate(db: Session, email: str, password: str) -> User:
    now = datetime.now(UTC)
    window = timedelta(minutes=settings.login_lockout_minutes)
    failures, oldest = login_failure_repository.recent(db, email, now - window)
    if oldest is not None and failures >= settings.login_max_failures:
        retry_after = max(1, math.ceil((oldest + window - now).total_seconds()))
        minutes = math.ceil(retry_after / 60)
        raise TooManyRequestsError(
            f"Too many failed sign-in attempts. Try again in {minutes} "
            f"minute{'s' if minutes != 1 else ''}.",
            "too_many_login_attempts",
            headers={"Retry-After": str(retry_after)},
        )

    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        login_failure_repository.add(db, email)
        login_failure_repository.delete_before(db, now - window)
        db.commit()
        raise UnauthorizedError("Invalid email or password", "invalid_credentials")

    login_failure_repository.delete_for_email(db, email)
    return user


def issue_tokens(db: Session, user: User) -> TokenPair:
    token = refresh_token_repository.add(
        db,
        RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
        ),
    )
    db.commit()
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id, token.id, token.expires_at),
    )


def rotate_refresh_token(db: Session, raw_token: str) -> tuple[User, TokenPair]:
    payload = decode_token(raw_token, "refresh")
    token = refresh_token_repository.get_by_id(db, uuid.UUID(payload["jti"]), lock=True)
    if token is None or token.revoked_at is not None or token.expires_at <= datetime.now(UTC):
        raise UnauthorizedError("Session has expired", "session_expired")
    user = user_repository.get_by_id(db, token.user_id)
    if user is None:
        raise UnauthorizedError("Session has expired", "session_expired")
    token.revoked_at = datetime.now(UTC)
    return user, issue_tokens(db, user)


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    try:
        payload = decode_token(raw_token, "refresh")
    except UnauthorizedError:
        return
    token = refresh_token_repository.get_by_id(db, uuid.UUID(payload["jti"]))
    if token is not None and token.revoked_at is None:
        token.revoked_at = datetime.now(UTC)
        db.commit()


def change_password(db: Session, user: User, data: ChangePasswordIn) -> TokenPair:
    if not verify_password(data.current_password, user.password_hash):
        raise AppError("Current password is incorrect", "invalid_password")
    user.password_hash = hash_password(data.new_password)
    refresh_token_repository.revoke_all_for_user(db, user.id, datetime.now(UTC))
    return issue_tokens(db, user)
