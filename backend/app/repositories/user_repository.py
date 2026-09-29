from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Role, User
from app.repositories.pagination import paginate
from app.schemas.user import UserQuery


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


def list_page(db: Session, query: UserQuery) -> dict[str, Any]:
    stmt = select(User).order_by(User.full_name)
    if query.role:
        stmt = stmt.where(User.role == query.role)
    if query.search:
        pattern = f"%{query.search}%"
        stmt = stmt.where(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))
    return paginate(db, stmt, query)
