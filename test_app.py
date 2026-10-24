import pytest
from fastapi.testclient import TestClient

import app_final
from app_final import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_state():
    app_final.tasks.clear()
    app_final.counter["next_id"] = 1

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_create_and_get_task():
    response = client.post("/tasks", json={"title": "Купить хлеб", "priority": "high"})
    assert response.status_code == 201
    task_id = response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Купить хлеб"
    assert response.json()["done"] is False

def test_get_missing_task_returns_404():
    response = client.get("/tasks/999")
    assert response.status_code == 404

def test_create_task_with_empty_title_returns_422():
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422

def test_complete_task_and_filter_by_done():
    client.post("/tasks", json={"title": "Задача 1"})
    client.post("/tasks", json={"title": "Задача 2"})
    client.post("/tasks/1/done")
    done_tasks = client.get("/tasks", params={"done": True}).json()
    assert len(done_tasks) == 1
    assert done_tasks[0]["id"] == 1

def test_stats():
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B"})
    client.post("/tasks/1/done")

    assert client.get("/stats").json() == {"total": 2, "done": 1, "active": 1}