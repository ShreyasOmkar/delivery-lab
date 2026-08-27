import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_endpoints_response_time():
    """Test that health endpoints respond quickly"""
    import time
    
    endpoints = ["/health/live", "/health/ready"]
    for endpoint in endpoints:
        start = time.time()
        response = client.get(endpoint)
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1, f"{endpoint} took {elapsed} seconds"


def test_liveness_format():
    """Test liveness response format is consistent"""
    response = client.get("/health/live")
    data = response.json()
    assert "alive" in data
    assert "status" in data
    assert data["status"] == "ok"


def test_readiness_format():
    """Test readiness response format is consistent"""
    response = client.get("/health/ready")
    data = response.json()
    assert "ready" in data
    assert "status" in data
    assert data["status"] == "ok"


def test_health_headers():
    """Test health endpoints have correct headers"""
    for endpoint in ["/health/live", "/health/ready"]:
        response = client.get(endpoint)
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"