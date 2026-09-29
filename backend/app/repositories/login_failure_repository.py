from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import LoginFailure


def recent(db: Session, email: str, since: datetime) -> tuple[int, datetime | None]:
    count, oldest = db.execute(
        select(func.count(), func.min(LoginFailure.created_at)).where(
            LoginFailure.email == email, LoginFailure.created_at >= since
        )
    ).one()
    return count, oldest


def add(db: Session, email: str) -> None:
    db.add(LoginFailure(email=email))


def delete_for_email(db: Session, email: str) -> None:
    db.execute(delete(LoginFailure).where(LoginFailure.email == email))


def delete_before(db: Session, cutoff: datetime) -> None:
    db.execute(delete(LoginFailure).where(LoginFailure.created_at < cutoff))
