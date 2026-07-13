from datetime import date, timedelta

import pytest


async def seed(client, auth_headers):
    resp = await client.post("/api/v1/learning/seed-defaults", headers=auth_headers)
    assert resp.status_code == 200
    return resp.json()


@pytest.mark.asyncio
async def test_seed_defaults_creates_two_tracks(client, auth_headers):
    tracks = await seed(client, auth_headers)
    assert len(tracks) == 2
    slugs = {t["slug"] for t in tracks}
    assert slugs == {"python-bootcamp", "french-a1-clb7"}
    assert all(t["items_total"] > 0 for t in tracks)
    assert all(t["items_done"] == 0 for t in tracks)


@pytest.mark.asyncio
async def test_seed_defaults_is_idempotent(client, auth_headers):
    first = await seed(client, auth_headers)
    second = await seed(client, auth_headers)
    assert {t["id"] for t in first} == {t["id"] for t in second}

    resp = await client.get("/api/v1/learning/tracks", headers=auth_headers)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_track_detail_has_items_and_routines(client, auth_headers):
    tracks = await seed(client, auth_headers)
    french = next(t for t in tracks if t["slug"] == "french-a1-clb7")

    resp = await client.get(
        f"/api/v1/learning/tracks/{french['id']}", headers=auth_headers
    )
    assert resp.status_code == 200
    detail = resp.json()
    assert len(detail["items"]) == detail["items_total"]
    routine_names = [r["name"] for r in detail["routines"]]
    assert routine_names == [
        "Cartoon listening + shadowing",
        "Textbook / grammar",
        "Anki",
    ]
    anki = detail["routines"][2]
    assert anki["rest_weekdays"] == []
    assert anki["today_done"] is False
    assert anki["streak"] == 0


@pytest.mark.asyncio
async def test_toggle_item(client, auth_headers):
    tracks = await seed(client, auth_headers)
    python = next(t for t in tracks if t["slug"] == "python-bootcamp")
    detail = (
        await client.get(f"/api/v1/learning/tracks/{python['id']}", headers=auth_headers)
    ).json()
    item = detail["items"][0]

    resp = await client.post(
        f"/api/v1/learning/items/{item['id']}/toggle", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"
    assert resp.json()["completed_at"] is not None

    detail = (
        await client.get(f"/api/v1/learning/tracks/{python['id']}", headers=auth_headers)
    ).json()
    assert detail["items_done"] == 1

    resp = await client.post(
        f"/api/v1/learning/items/{item['id']}/toggle", headers=auth_headers
    )
    assert resp.json()["status"] == "PENDING"
    assert resp.json()["completed_at"] is None


@pytest.mark.asyncio
async def test_log_and_unlog_practice(client, auth_headers):
    tracks = await seed(client, auth_headers)
    french = next(t for t in tracks if t["slug"] == "french-a1-clb7")
    detail = (
        await client.get(f"/api/v1/learning/tracks/{french['id']}", headers=auth_headers)
    ).json()
    anki = next(r for r in detail["routines"] if r["name"] == "Anki")

    # Log yesterday and today → streak of 2
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = await client.post(
        f"/api/v1/learning/routines/{anki['id']}/log",
        json={"log_date": yesterday},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    resp = await client.post(
        f"/api/v1/learning/routines/{anki['id']}/log",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    # Defaults to the routine's configured minutes
    assert resp.json()["minutes"] == 15

    # Re-logging the same day is an upsert, not a duplicate
    resp = await client.post(
        f"/api/v1/learning/routines/{anki['id']}/log",
        json={"minutes": 30},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["minutes"] == 30

    detail = (
        await client.get(f"/api/v1/learning/tracks/{french['id']}", headers=auth_headers)
    ).json()
    anki = next(r for r in detail["routines"] if r["name"] == "Anki")
    assert anki["today_done"] is True
    assert anki["today_minutes"] == 30
    assert anki["streak"] == 2

    # Unlog today → streak drops to 1 (yesterday), today no longer done
    resp = await client.delete(
        f"/api/v1/learning/routines/{anki['id']}/log", headers=auth_headers
    )
    assert resp.status_code == 204
    detail = (
        await client.get(f"/api/v1/learning/tracks/{french['id']}", headers=auth_headers)
    ).json()
    anki = next(r for r in detail["routines"] if r["name"] == "Anki")
    assert anki["today_done"] is False
    assert anki["streak"] == 1


@pytest.mark.asyncio
async def test_track_of_other_user_is_404(client, auth_headers, db_session):
    import uuid
    from app.core.security import hash_password, create_access_token
    from app.models.user import User

    other = User(
        id=uuid.uuid4(),
        email="other@example.com",
        password_hash=hash_password("secret123"),
        stated_goal="",
        weekly_goal_hours_threshold=10,
    )
    db_session.add(other)
    await db_session.commit()
    other_headers = {"Authorization": f"Bearer {create_access_token(str(other.id))}"}

    tracks = await seed(client, auth_headers)
    resp = await client.get(
        f"/api/v1/learning/tracks/{tracks[0]['id']}", headers=other_headers
    )
    assert resp.status_code == 404
