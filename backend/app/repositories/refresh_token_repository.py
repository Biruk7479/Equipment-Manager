import uuid
from datetime import datetime

from sqlalchemy import update
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
