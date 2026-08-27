import os
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_index():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "delivery-lab"
    assert "version" in data

def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True

def test_readiness_default():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True

def test_readiness_not_ready():
    os.environ["READY"] = "false"  
    import importlib
    import app as app_module
    importlib.reload(app_module)   
    from app import app as reloaded_app
    client_reloaded = TestClient(reloaded_app)    
    response = client_reloaded.get("/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["ready"] is False  
    os.environ["READY"] = "true"

def test_work_no_delay():
    response = client.get("/work")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["delay_seconds"] == 0

def test_work_with_delay():
    os.environ["WORK_DELAY"] = "0.5"
    import importlib
    import app as app_module
    importlib.reload(app_module)
    from app import app as reloaded_app
    client_reloaded = TestClient(reloaded_app) 
    import time
    start = time.time()
    response = client_reloaded.get("/work")
    elapsed = time.time() - start   
    assert response.status_code == 200
    assert elapsed >= 0.5
    data = response.json()
    assert data["delay_seconds"] == 0.5
    os.environ["WORK_DELAY"] = "0"

def test_config_endpoint():  
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "app_version" in data
    assert "work_delay" in data
    assert "ready" in data