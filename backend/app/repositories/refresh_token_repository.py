import uuid

from sqlalchemy.orm import Session

from app.models import RefreshToken


def get_by_id(db: Session, token_id: uuid.UUID, lock: bool = False) -> RefreshToken | None:
    return db.get(RefreshToken, token_id, with_for_update=lock)


def add(db: Session, token: RefreshToken) -> RefreshToken:
    db.add(token)
    db.flush()
    return token
