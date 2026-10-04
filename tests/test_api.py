"""API Tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Vgas" in response.json()["message"]

def test_plans():
    response = client.get("/api/v1/plans")
    assert response.status_code == 200
    assert len(response.json()["plans"]) == 3

def test_leaderboard():
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    assert "deals" in response.json()
