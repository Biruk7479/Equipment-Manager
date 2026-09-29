from fastapi.testclient import TestClient

from tests.conftest import PASSWORD


def test_manager_can_create_manager_account(manager: TestClient) -> None:
    response = manager.post(
        "/api/v1/users",
        json={
            "email": "lead@test.com",
            "full_name": "Lead",
            "password": PASSWORD,
            "role": "manager",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "manager"


def test_manager_can_filter_users(manager: TestClient, employee: TestClient) -> None:
    response = manager.get("/api/v1/users", params={"role": "employee"})

    assert response.status_code == 200
    assert [u["email"] for u in response.json()["items"]] == ["employee@test.com"]


def test_employee_cannot_manage_users(employee: TestClient) -> None:
    create = employee.post(
        "/api/v1/users",
        json={"email": "x@test.com", "full_name": "X", "password": PASSWORD, "role": "manager"},
    )

    assert create.status_code == 403
    assert employee.get("/api/v1/users").status_code == 403
