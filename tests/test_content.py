import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# ── /domains ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_domains_returns_envelope(mock_empty_db, http):
    async with http as c:
        r = await c.get("/domains")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert body["error"] is None


# ── /domains/{id}/modules ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_domain_not_found(mock_empty_db, http):
    async with http as c:
        r = await c.get("/domains/does-not-exist/modules")
    assert r.status_code == 404


# ── /modules/{id} ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_module_not_found(mock_empty_db, http):
    async with http as c:
        r = await c.get("/modules/does-not-exist")
    assert r.status_code == 404


# ── /modules/{id}/content ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_content_rejects_unknown_file_param(http):
    async with http as c:
        r = await c.get("/modules/any-id/content?file=../../etc/passwd")
    assert r.status_code == 400
    assert "file must be one of" in r.json()["detail"]


@pytest.mark.asyncio
async def test_content_rejects_arbitrary_filename(http):
    async with http as c:
        r = await c.get("/modules/any-id/content?file=server")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_content_module_not_found(mock_empty_db, http):
    async with http as c:
        r = await c.get("/modules/does-not-exist/content?file=readme")
    assert r.status_code == 404


# ── /modules/{id}/notebooks ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_notebooks_module_not_found(mock_empty_db, http):
    async with http as c:
        r = await c.get("/modules/does-not-exist/notebooks")
    assert r.status_code == 404


# ── /search ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_empty_query_returns_envelope(mock_empty_db, http):
    async with http as c:
        r = await c.get("/search")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert body["meta"]["page"] == 1


@pytest.mark.asyncio
async def test_search_pagination_params(mock_empty_db, http):
    async with http as c:
        r = await c.get("/search?page=2&limit=5")
    assert r.status_code == 200
    assert r.json()["meta"]["limit"] == 5
    assert r.json()["meta"]["page"] == 2


# ── CORS ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cors_allows_localhost_3000(http):
    async with http as c:
        r = await c.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert r.status_code == 200
    assert "access-control-allow-origin" in r.headers


@pytest.mark.asyncio
async def test_cors_get_includes_allow_origin(http):
    async with http as c:
        r = await c.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.asyncio
async def test_cors_rejects_unknown_origin(http):
    async with http as c:
        r = await c.get("/health", headers={"Origin": "http://evil.example.com"})
    assert "access-control-allow-origin" not in r.headers
