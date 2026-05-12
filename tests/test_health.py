import pytest


@pytest.mark.asyncio
async def test_health(http):
    async with http as c:
        r = await c.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
