import pytest


@pytest.mark.asyncio
async def test_sync_requires_secret(http):
    async with http as c:
        r = await c.post("/sync/trigger")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_sync_rejects_wrong_secret(http):
    async with http as c:
        r = await c.post("/sync/trigger", headers={"x-sync-secret": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_sync_status_returns_envelope(mock_empty_db, http):
    async with http as c:
        r = await c.get("/sync/status")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
