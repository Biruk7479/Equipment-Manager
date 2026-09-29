import logging

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import PASSWORD, login


def refresh(client: TestClient) -> int:
    return client.post("/api/v1/auth/refresh").status_code


def me(client: TestClient) -> int:
    return client.get("/api/v1/auth/me").status_code


def with_refresh_token(token: str) -> TestClient:
    client = TestClient(app)
    client.cookies.set("refresh_token", token)
    return client


def test_rotation_keeps_working_across_many_refreshes(employee: TestClient) -> None:
    assert [refresh(employee) for _ in range(3)] == [200, 200, 200]
    assert me(employee) == 200


def test_replaying_a_rotated_token_signs_the_user_out_everywhere(
    employee: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    other_device = login("employee@test.com")
    stolen = employee.cookies.get("refresh_token")
    assert refresh(employee) == 200

    with caplog.at_level(logging.WARNING):
        assert refresh(with_refresh_token(stolen)) == 401

    assert "Refresh token reuse" in caplog.text
    assert (refresh(employee), me(employee)) == (401, 401)
    assert (refresh(other_device), me(other_device)) == (401, 401)


def test_attacker_who_refreshes_first_is_cut_off_when_the_user_refreshes(
    employee: TestClient,
) -> None:
    attacker = with_refresh_token(employee.cookies.get("refresh_token"))
    assert refresh(attacker) == 200
    assert me(attacker) == 200

    assert refresh(employee) == 401

    assert (refresh(attacker), me(attacker)) == (401, 401)


def test_replaying_a_signed_out_token_does_not_affect_other_sessions(
    employee: TestClient,
) -> None:
    other_device = login("employee@test.com")
    signed_out = employee.cookies.get("refresh_token")
    employee.post("/api/v1/auth/logout")

    assert refresh(with_refresh_token(signed_out)) == 401

    assert (me(other_device), refresh(other_device)) == (200, 200)


def test_other_devices_refreshing_after_password_change_keep_the_current_session(
    employee: TestClient,
) -> None:
    other_device = login("employee@test.com")
    employee.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": "NewPassword456"},
    )

    assert refresh(other_device) == 401

    assert (me(employee), refresh(employee)) == (200, 200)
