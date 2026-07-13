import pytest


@pytest.mark.asyncio
async def test_create_priority(client, auth_headers):
    resp = await client.post(
        "/api/v1/priorities",
        json={
            "title": "Ship POS MVP",
            "track": "TECHNICAL",
            "definition_of_done": "Deployed with auth + time blocks",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Ship POS MVP"
    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_second_active_same_track_409(client, auth_headers):
    # First priority
    await client.post(
        "/api/v1/priorities",
        json={
            "title": "First",
            "track": "TECHNICAL",
            "definition_of_done": "Done",
        },
        headers=auth_headers,
    )

    # Second on same track → 409
    resp = await client.post(
        "/api/v1/priorities",
        json={
            "title": "Second",
            "track": "TECHNICAL",
            "definition_of_done": "Also done",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["detail"]["error"] == "PRIORITY_CAP"


@pytest.mark.asyncio
async def test_cut_priority(client, auth_headers):
    # Create
    create_resp = await client.post(
        "/api/v1/priorities",
        json={
            "title": "To cut",
            "track": "LANGUAGE",
            "definition_of_done": "Something",
        },
        headers=auth_headers,
    )
    priority_id = create_resp.json()["id"]

    # Cut
    resp = await client.post(
        f"/api/v1/priorities/{priority_id}/cut",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CUT"


@pytest.mark.asyncio
async def test_list_priorities(client, auth_headers):
    resp = await client.get("/api/v1/priorities", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
