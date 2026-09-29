from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Role, User
from app.repositories import user_repository


def seed_manager() -> None:
    if not settings.manager_email or not settings.manager_password:
        return
    with SessionLocal() as db:
        if user_repository.exists_with_role(db, Role.MANAGER):
            return
        user_repository.add(
            db,
            User(
                email=settings.manager_email.lower(),
                full_name=settings.manager_name,
                password_hash=hash_password(settings.manager_password),
                role=Role.MANAGER,
            ),
        )
        db.commit()
        print(f"Seeded manager account {settings.manager_email}")


if __name__ == "__main__":
    seed_manager()
