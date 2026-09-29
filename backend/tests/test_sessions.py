from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from tests.conftest import PASSWORD, login


def me(client: TestClient, access_token: str | None = None) -> int:
    if access_token is not None:
        client.cookies.set("access_token", access_token)
    return client.get("/api/v1/auth/me").status_code


def test_logout_invalidates_the_access_token_immediately(employee: TestClient) -> None:
    access_token = employee.cookies.get("access_token")

    employee.post("/api/v1/auth/logout")

    assert me(TestClient(app), access_token) == 401


def test_password_change_invalidates_other_sessions_immediately(employee: TestClient) -> None:
    other = login("employee@test.com")
    assert me(other) == 200

    employee.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": "NewPassword456"},
    )

    assert me(other) == 401
    assert me(employee) == 200


def test_logout_only_ends_its_own_session(employee: TestClient) -> None:
    other = login("employee@test.com")

    employee.post("/api/v1/auth/logout")

    assert me(other) == 200


def test_access_token_stays_valid_across_refresh_in_the_same_session(
    employee: TestClient,
) -> None:
    before_refresh = employee.cookies.get("access_token")

    assert employee.post("/api/v1/auth/refresh").status_code == 200

    assert me(TestClient(app), before_refresh) == 200


def test_access_token_without_a_session_is_rejected(employee: TestClient) -> None:
    user_id = employee.get("/api/v1/auth/me").json()["id"]
    token = jwt.encode(
        {"sub": str(user_id), "type": "access", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    assert me(TestClient(app), token) == 401
