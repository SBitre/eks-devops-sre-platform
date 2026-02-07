"""Tests for the DevOps SRE Platform API."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_liveness(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.anyio
async def test_docs_accessible(client):
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_deployment(client):
    payload = {
        "service_name": "test-service",
        "environment": "staging",
        "version": "v1.0.0",
        "commit_sha": "abc123def456",
        "deployed_by": "pytest",
    }
    response = await client.post("/api/v1/deployments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["service_name"] == "test-service"
    assert data["status"] == "pending"


@pytest.mark.anyio
async def test_create_incident(client):
    payload = {
        "title": "Test incident",
        "severity": "sev3",
        "service_name": "test-service",
        "environment": "staging",
    }
    response = await client.post("/api/v1/incidents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test incident"
    assert data["status"] == "triggered"


@pytest.mark.anyio
async def test_create_slo(client):
    payload = {
        "service_name": "test-service",
        "name": "Availability SLO",
        "sli_type": "availability",
        "target_percentage": 99.9,
    }
    response = await client.post("/api/v1/slos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["target_percentage"] == 99.9


@pytest.mark.anyio
async def test_dora_metrics(client):
    response = await client.get("/api/v1/metrics/dora?environment=production&days=30")
    assert response.status_code == 200
    data = response.json()
    assert "deployment_frequency" in data
    assert "change_failure_rate" in data
    assert "mttr_hours" in data
    assert "rating" in data


@pytest.mark.anyio
async def test_metrics_endpoint(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
