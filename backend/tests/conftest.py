import os
from collections.abc import Callable, Iterator
from pathlib import Path

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://equipment:equipment@localhost:5433/equipment_test"
)
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256"

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models import Role, User

PASSWORD = "Password123"


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    command.upgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "head")


@pytest.fixture(autouse=True)
def clean_tables() -> Iterator[None]:
    yield
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


def create_user(email: str, role: Role = Role.EMPLOYEE) -> User:
    with SessionLocal() as db:
        user = User(
            email=email,
            full_name=email.split("@")[0],
            password_hash=hash_password(PASSWORD),
            role=role,
        )
        db.add(user)
        db.commit()
        return user


def login(email: str) -> TestClient:
    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return client


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def make_client() -> Callable[[str, Role], TestClient]:
    def factory(email: str, role: Role = Role.EMPLOYEE) -> TestClient:
        create_user(email, role)
        return login(email)

    return factory


@pytest.fixture
def manager(make_client: Callable[[str, Role], TestClient]) -> TestClient:
    return make_client("manager@test.com", Role.MANAGER)


@pytest.fixture
def employee(make_client: Callable[[str, Role], TestClient]) -> TestClient:
    return make_client("employee@test.com", Role.EMPLOYEE)
