from fastapi.testclient import TestClient

LAPTOP = {
    "name": "ThinkPad X1",
    "category": "laptop",
    "description": "14-inch business laptop",
    "available_quantity": 5,
}


def create(client: TestClient, **overrides: object) -> dict:
    response = client.post("/api/v1/equipment", json={**LAPTOP, **overrides})
    assert response.status_code == 201
    return response.json()


def test_manager_can_create_and_edit_equipment(manager: TestClient) -> None:
    equipment = create(manager)

    response = manager.put(
        f"/api/v1/equipment/{equipment['id']}", json={**LAPTOP, "available_quantity": 8}
    )

    assert response.status_code == 200
    assert response.json()["available_quantity"] == 8


def test_employee_can_view_but_not_modify(manager: TestClient, employee: TestClient) -> None:
    equipment = create(manager)

    assert employee.get(f"/api/v1/equipment/{equipment['id']}").status_code == 200
    assert employee.post("/api/v1/equipment", json=LAPTOP).status_code == 403
    assert employee.put(f"/api/v1/equipment/{equipment['id']}", json=LAPTOP).status_code == 403


def test_quantity_cannot_be_negative(manager: TestClient) -> None:
    response = manager.post("/api/v1/equipment", json={**LAPTOP, "available_quantity": -1})

    assert response.status_code == 422
    assert response.json()["error"]["details"][0]["field"] == "available_quantity"


def test_duplicate_name_is_rejected_case_insensitively(manager: TestClient) -> None:
    create(manager)
    response = manager.post("/api/v1/equipment", json={**LAPTOP, "name": "thinkpad x1"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "equipment_name_taken"


def test_invalid_category_is_rejected(manager: TestClient) -> None:
    response = manager.post("/api/v1/equipment", json={**LAPTOP, "category": "printer"})

    assert response.status_code == 422


def test_missing_equipment_returns_404(employee: TestClient) -> None:
    response = employee.get("/api/v1/equipment/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_search_filter_and_paginate(manager: TestClient) -> None:
    create(manager)
    create(manager, name="Dell UltraSharp 27", category="monitor", available_quantity=0)
    create(manager, name="Dell Latitude", available_quantity=2)

    search = manager.get("/api/v1/equipment", params={"search": "dell"}).json()
    assert {item["name"] for item in search["items"]} == {"Dell UltraSharp 27", "Dell Latitude"}

    by_category = manager.get("/api/v1/equipment", params={"category": "monitor"}).json()
    assert [item["name"] for item in by_category["items"]] == ["Dell UltraSharp 27"]

    unavailable = manager.get("/api/v1/equipment", params={"available": False}).json()
    assert [item["name"] for item in unavailable["items"]] == ["Dell UltraSharp 27"]

    page = manager.get("/api/v1/equipment", params={"page": 2, "page_size": 2}).json()
    assert page["total"] == 3
    assert [item["name"] for item in page["items"]] == ["ThinkPad X1"]
