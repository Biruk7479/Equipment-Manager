from fastapi.testclient import TestClient

from tests.conftest import PASSWORD

REGISTER = {"email": "New.User@Test.com", "full_name": "New User", "password": PASSWORD}


def test_register_creates_employee_and_logs_in(client: TestClient) -> None:
    response = client.post("/api/v1/auth/register", json=REGISTER)

    assert response.status_code == 201
    assert response.json()["role"] == "employee"
    assert response.json()["email"] == "new.user@test.com"
    assert client.get("/api/v1/auth/me").status_code == 200


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=REGISTER)
    response = client.post("/api/v1/auth/register", json={**REGISTER, "email": "new.user@test.com"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_taken"


def test_register_rejects_role_field(client: TestClient) -> None:
    response = client.post("/api/v1/auth/register", json={**REGISTER, "role": "manager"})

    assert response.status_code == 422
    assert response.json()["error"]["details"][0]["field"] == "role"


def test_login_with_wrong_password_fails(client: TestClient, employee: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login", json={"email": "employee@test.com", "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_protected_route_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "unauthorized", "message": "Not authenticated", "details": None}
    }


def test_refresh_rotates_token_and_rejects_reuse(employee: TestClient) -> None:
    old_refresh = employee.cookies.get("refresh_token")

    assert employee.post("/api/v1/auth/refresh").status_code == 200
    assert employee.cookies.get("refresh_token") != old_refresh

    employee.cookies.set("refresh_token", old_refresh)
    assert employee.post("/api/v1/auth/refresh").status_code == 401


def test_logout_revokes_session(employee: TestClient) -> None:
    refresh_token = employee.cookies.get("refresh_token")

    assert employee.post("/api/v1/auth/logout").status_code == 204
    assert employee.get("/api/v1/auth/me").status_code == 401

    employee.cookies.set("refresh_token", refresh_token)
    assert employee.post("/api/v1/auth/refresh").status_code == 401


def test_change_password_revokes_other_sessions(employee: TestClient, client: TestClient) -> None:
    client.post("/api/v1/auth/login", json={"email": "employee@test.com", "password": PASSWORD})

    response = employee.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": "NewPassword456"},
    )

    assert response.status_code == 204
    assert employee.post("/api/v1/auth/refresh").status_code == 200
    assert client.post("/api/v1/auth/refresh").status_code == 401
    login = client.post(
        "/api/v1/auth/login", json={"email": "employee@test.com", "password": "NewPassword456"}
    )
    assert login.status_code == 200


def test_change_password_requires_current_password(employee: TestClient) -> None:
    response = employee.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong-password", "new_password": "NewPassword456"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_password"
