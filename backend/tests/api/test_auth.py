import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_register_duplicate(client, test_user):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_no_token(client):
    resp = await client.get("/api/v1/time-blocks")
    assert resp.status_code in (401, 403)
