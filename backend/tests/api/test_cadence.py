import pytest


@pytest.mark.asyncio
async def test_create_quarter(client, auth_headers):
    resp = await client.post(
        "/api/v1/cadence/quarters",
        json={"year": 2026, "quarter_num": 3, "theme": "Backend mastery"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["year"] == 2026
    assert data["quarter_num"] == 3
    assert data["phase"] == "REST"


@pytest.mark.asyncio
async def test_get_current_quarter(client, auth_headers):
    # Create one first
    await client.post(
        "/api/v1/cadence/quarters",
        json={"year": 2026, "quarter_num": 3, "theme": "Test"},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/cadence/current", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["phase"] == "REST"


@pytest.mark.asyncio
async def test_cadence_tick(client, auth_headers):
    await client.post(
        "/api/v1/cadence/quarters",
        json={"year": 2026, "quarter_num": 3},
        headers=auth_headers,
    )
    resp = await client.post("/api/v1/cadence/tick", headers=auth_headers)
    assert resp.status_code == 200
