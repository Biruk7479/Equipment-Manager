from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.core.security import hash_password
from app.models import Role, User
from app.repositories import user_repository
from app.schemas.auth import RegisterIn


def create_user(db: Session, data: RegisterIn, role: Role) -> User:
    if user_repository.get_by_email(db, data.email):
        raise ConflictError("An account with this email already exists", "email_taken")
    user = user_repository.add(
        db,
        User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            role=role,
        ),
    )
    db.commit()
    return user
