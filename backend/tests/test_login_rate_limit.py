import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import engine
from tests.conftest import PASSWORD

EMAIL = "employee@test.com"


def attempt(client: TestClient, email: str = EMAIL, password: str = "wrong-password") -> int:
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    ).status_code


def age_failures(minutes: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE login_failures SET created_at = created_at - make_interval(mins => :m)"),
            {"m": minutes},
        )


def failure_count() -> int:
    with engine.connect() as conn:
        return conn.execute(text("SELECT count(*) FROM login_failures")).scalar_one()


@pytest.mark.usefixtures("employee")
def test_account_is_locked_after_five_failures(client: TestClient) -> None:
    assert [attempt(client) for _ in range(5)] == [401] * 5

    response = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "too_many_login_attempts"
    assert "15 minutes" in response.json()["error"]["message"]
    assert 0 < int(response.headers["Retry-After"]) <= 900


@pytest.mark.usefixtures("employee")
def test_lock_only_applies_to_that_account(client: TestClient, manager: TestClient) -> None:
    for _ in range(5):
        attempt(client)

    assert attempt(client, EMAIL, PASSWORD) == 429
    assert attempt(client, "manager@test.com", PASSWORD) == 200


def test_unknown_emails_are_limited_the_same_way(client: TestClient) -> None:
    assert [attempt(client, "ghost@test.com") for _ in range(6)] == [401] * 5 + [429]


@pytest.mark.usefixtures("employee")
def test_changing_email_case_does_not_bypass_the_limit(client: TestClient) -> None:
    for email in ("Employee@Test.com", "EMPLOYEE@TEST.COM", "employee@TEST.com", EMAIL, EMAIL):
        attempt(client, email)

    assert attempt(client, EMAIL, PASSWORD) == 429


@pytest.mark.usefixtures("employee")
def test_successful_sign_in_resets_the_failure_count(client: TestClient) -> None:
    for _ in range(4):
        attempt(client)
    assert attempt(client, EMAIL, PASSWORD) == 200

    for _ in range(4):
        attempt(client)
    assert attempt(client, EMAIL, PASSWORD) == 200


@pytest.mark.usefixtures("employee")
def test_lock_expires_after_the_window(client: TestClient) -> None:
    for _ in range(5):
        attempt(client)
    assert attempt(client, EMAIL, PASSWORD) == 429

    age_failures(16)

    assert attempt(client, EMAIL, PASSWORD) == 200


@pytest.mark.usefixtures("employee")
def test_retry_after_counts_down_from_the_oldest_failure(client: TestClient) -> None:
    for _ in range(5):
        attempt(client)
    age_failures(10)

    response = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})

    assert response.status_code == 429
    assert 290 <= int(response.headers["Retry-After"]) <= 300
    assert "5 minutes" in response.json()["error"]["message"]


def test_expired_failures_are_pruned(client: TestClient) -> None:
    for _ in range(3):
        attempt(client, "ghost@test.com")
    age_failures(20)

    attempt(client, "other@test.com")

    assert failure_count() == 1
