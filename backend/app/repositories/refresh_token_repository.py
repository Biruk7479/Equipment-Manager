import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import RefreshToken


def get_by_id(db: Session, token_id: uuid.UUID, lock: bool = False) -> RefreshToken | None:
    return db.get(RefreshToken, token_id, with_for_update=lock)


def add(db: Session, token: RefreshToken) -> RefreshToken:
    db.add(token)
    db.flush()
    return token


def revoke_all_for_user(db: Session, user_id: int, revoked_at: datetime) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=revoked_at)
    )


def session_is_active(db: Session, session_id: uuid.UUID, user_id: int, now: datetime) -> bool:
    stmt = select(RefreshToken.id).where(
        RefreshToken.session_id == session_id,
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
        RefreshToken.expires_at > now,
    )
    return db.scalar(stmt.limit(1)) is not None
