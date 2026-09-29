from collections.abc import Callable

from fastapi.testclient import TestClient

from app.models import Role


def test_dashboard_summarizes_equipment_and_requests(
    make_client: Callable[[str, Role], TestClient], employee: TestClient, manager: TestClient
) -> None:
    other = make_client("other@test.com", Role.EMPLOYEE)
    laptop = manager.post(
        "/api/v1/equipment",
        json={"name": "ThinkPad", "category": "laptop", "available_quantity": 4},
    ).json()
    headset = manager.post(
        "/api/v1/equipment", json={"name": "Jabra", "category": "headset", "available_quantity": 6}
    ).json()
    body = {"quantity": 1, "justification": "Needed for onboarding"}
    approved = employee.post("/api/v1/requests", json={**body, "equipment_id": laptop["id"]}).json()
    employee.post("/api/v1/requests", json={**body, "equipment_id": headset["id"]})
    rejected = other.post("/api/v1/requests", json={**body, "equipment_id": laptop["id"]}).json()
    manager.post(f"/api/v1/requests/{approved['id']}/approve")
    manager.post(f"/api/v1/requests/{rejected['id']}/reject", json={"comment": "No stock plan"})

    summary = manager.get("/api/v1/dashboard").json()

    assert summary["total_equipment"] == 2
    assert summary["total_available_quantity"] == 9
    assert summary["requests"] == {"pending": 1, "approved": 1, "rejected": 1}
    by_category = {row["category"]: row for row in summary["requests_by_category"]}
    assert len(by_category) == 5
    assert (by_category["laptop"]["approved"], by_category["laptop"]["rejected"]) == (1, 1)
    assert by_category["headset"]["pending"] == 1

    own = employee.get("/api/v1/dashboard").json()
    assert own["requests"] == {"pending": 1, "approved": 1, "rejected": 0}
