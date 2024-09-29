from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    data = response.json()
    assert data["status"] == "pass"
    assert data["version"] == "1.0"
    assert data["releaseId"] == "1.1"


def test_get_health_error() -> None:
    # test for health error
    pass
