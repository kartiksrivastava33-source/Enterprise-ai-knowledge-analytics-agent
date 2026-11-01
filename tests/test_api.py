
import sys
from pathlib import Path

# Add project root to Python's import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_empty_question():
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 422


def test_missing_question():
    response = client.post("/ask", json={})

    assert response.status_code == 422
