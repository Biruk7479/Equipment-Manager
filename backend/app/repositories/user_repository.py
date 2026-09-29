from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role, User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def exists_with_role(db: Session, role: Role) -> bool:
    return db.scalar(select(User.id).where(User.role == role).limit(1)) is not None


def add(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user
