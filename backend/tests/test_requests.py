from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db.session import engine
from app.models import Role
from app.services import request_service


@pytest.fixture
def laptop(manager: TestClient) -> dict:
    return manager.post(
        "/api/v1/equipment",
        json={"name": "ThinkPad", "category": "laptop", "available_quantity": 3},
    ).json()


def submit(client: TestClient, equipment_id: int, quantity: int = 1) -> dict:
    response = client.post(
        "/api/v1/requests",
        json={
            "equipment_id": equipment_id,
            "quantity": quantity,
            "justification": "Needed for onboarding",
        },
    )
    assert response.status_code == 201
    return response.json()


def stock(client: TestClient, equipment_id: int) -> int:
    return client.get(f"/api/v1/equipment/{equipment_id}").json()["available_quantity"]


def test_new_request_starts_pending(employee: TestClient, laptop: dict) -> None:
    request = submit(employee, laptop["id"])

    assert request["status"] == "pending"
    assert request["requester"]["email"] == "employee@test.com"


@pytest.mark.parametrize(
    "payload",
    [
        {"quantity": 0},
        {"quantity": -2},
        {"justification": "   "},
        {"status": "approved"},
        {"requester_id": 99},
        {"reviewer_id": 1},
    ],
)
def test_invalid_or_protected_fields_are_rejected(
    employee: TestClient, laptop: dict, payload: dict
) -> None:
    body = {"equipment_id": laptop["id"], "quantity": 1, "justification": "Needed for onboarding"}

    response = employee.post("/api/v1/requests", json={**body, **payload})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_duplicate_pending_request_is_rejected(employee: TestClient, laptop: dict) -> None:
    submit(employee, laptop["id"])

    response = employee.post(
        "/api/v1/requests",
        json={"equipment_id": laptop["id"], "quantity": 1, "justification": "Needed again please"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_pending_request"


def test_managers_cannot_submit_requests(manager: TestClient, laptop: dict) -> None:
    response = manager.post(
        "/api/v1/requests",
        json={
            "equipment_id": laptop["id"],
            "quantity": 1,
            "justification": "Needed for onboarding",
        },
    )

    assert response.status_code == 403


def test_employees_only_access_their_own_requests(
    make_client: Callable[[str, Role], TestClient],
    employee: TestClient,
    manager: TestClient,
    laptop: dict,
) -> None:
    other = make_client("other@test.com", Role.EMPLOYEE)
    own = submit(employee, laptop["id"])
    foreign = submit(other, laptop["id"])

    listed = employee.get("/api/v1/requests").json()
    assert [r["id"] for r in listed["items"]] == [own["id"]]

    spoofed = employee.get("/api/v1/requests", params={"employee_id": foreign["requester"]["id"]})
    assert spoofed.json()["items"] == []

    assert employee.get(f"/api/v1/requests/{foreign['id']}").status_code == 404
    assert employee.get(f"/api/v1/requests/{foreign['id']}/history").status_code == 404
    assert manager.get("/api/v1/requests").json()["total"] == 2


def test_manager_filters_and_sorts_requests(
    make_client: Callable[[str, Role], TestClient],
    employee: TestClient,
    manager: TestClient,
    laptop: dict,
) -> None:
    monitor = manager.post(
        "/api/v1/equipment",
        json={"name": "Dell 27", "category": "monitor", "available_quantity": 1},
    ).json()
    first = submit(employee, laptop["id"])
    second = submit(employee, monitor["id"])
    third = submit(make_client("other@test.com", Role.EMPLOYEE), laptop["id"])
    manager.post(f"/api/v1/requests/{second['id']}/approve")

    def ids(**params: object) -> list[int]:
        return [r["id"] for r in manager.get("/api/v1/requests", params=params).json()["items"]]

    assert ids() == [third["id"], second["id"], first["id"]]
    assert ids(order="asc") == [first["id"], second["id"], third["id"]]
    assert ids(status="approved") == [second["id"]]
    assert ids(equipment_id=laptop["id"]) == [third["id"], first["id"]]
    assert ids(employee_id=first["requester"]["id"], status="pending") == [first["id"]]


def test_approval_reduces_stock_and_records_history(
    employee: TestClient, manager: TestClient, laptop: dict
) -> None:
    request = submit(employee, laptop["id"], quantity=2)

    response = manager.post(f"/api/v1/requests/{request['id']}/approve", json={"comment": "OK"})

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["reviewer"]["email"] == "manager@test.com"
    assert stock(manager, laptop["id"]) == 1

    history = employee.get(f"/api/v1/requests/{request['id']}/history").json()
    assert [(h["previous_status"], h["new_status"]) for h in history] == [
        (None, "pending"),
        ("pending", "approved"),
    ]
    assert history[1]["actor"]["email"] == "manager@test.com"
    assert history[1]["comment"] == "OK"


def test_approval_fails_when_stock_is_insufficient(
    employee: TestClient, manager: TestClient, laptop: dict
) -> None:
    request = submit(employee, laptop["id"], quantity=5)

    response = manager.post(f"/api/v1/requests/{request['id']}/approve")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "insufficient_stock"
    assert stock(manager, laptop["id"]) == 3
    assert manager.get(f"/api/v1/requests/{request['id']}").json()["status"] == "pending"


def test_approval_and_stock_update_roll_back_together(
    employee: TestClient, manager: TestClient, laptop: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = submit(employee, laptop["id"], quantity=2)

    def fail(*_: object) -> None:
        raise RuntimeError("history write failed")

    monkeypatch.setattr(request_service, "_apply_transition", fail)
    with pytest.raises(RuntimeError):
        manager.post(f"/api/v1/requests/{request['id']}/approve")

    assert stock(manager, laptop["id"]) == 3
    assert manager.get(f"/api/v1/requests/{request['id']}").json()["status"] == "pending"


def test_rejection_requires_comment(
    employee: TestClient, manager: TestClient, laptop: dict
) -> None:
    request = submit(employee, laptop["id"])

    missing = manager.post(f"/api/v1/requests/{request['id']}/reject", json={})
    blank = manager.post(f"/api/v1/requests/{request['id']}/reject", json={"comment": "  "})
    valid = manager.post(
        f"/api/v1/requests/{request['id']}/reject", json={"comment": "Budget freeze"}
    )

    assert missing.status_code == 422
    assert blank.status_code == 422
    assert valid.status_code == 200
    assert valid.json()["review_comment"] == "Budget freeze"
    assert stock(manager, laptop["id"]) == 3


@pytest.mark.parametrize("first", ["approve", "reject"])
@pytest.mark.parametrize("second", ["approve", "reject"])
def test_reviewed_requests_cannot_be_reviewed_again(
    employee: TestClient, manager: TestClient, laptop: dict, first: str, second: str
) -> None:
    request = submit(employee, laptop["id"])
    body = {"comment": "Reviewed"}
    manager.post(f"/api/v1/requests/{request['id']}/{first}", json=body)

    response = manager.post(f"/api/v1/requests/{request['id']}/{second}", json=body)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "invalid_status_transition"


def test_employees_cannot_review(employee: TestClient, laptop: dict) -> None:
    request = submit(employee, laptop["id"])

    assert employee.post(f"/api/v1/requests/{request['id']}/approve").status_code == 403
    reject = employee.post(f"/api/v1/requests/{request['id']}/reject", json={"comment": "No"})
    assert reject.status_code == 403


def test_history_cannot_be_modified_or_deleted(employee: TestClient, laptop: dict) -> None:
    submit(employee, laptop["id"])

    for statement in ("UPDATE request_history SET comment = 'x'", "DELETE FROM request_history"):
        with pytest.raises(DBAPIError, match="append-only"), engine.begin() as conn:
            conn.execute(text(statement))
