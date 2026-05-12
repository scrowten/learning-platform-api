from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import get_db


def make_mock_db(get_return=None, execute_return=None):
    """Return an async context manager that yields a mock DB session."""
    session = MagicMock()
    session.get = AsyncMock(return_value=get_return)

    result = MagicMock()
    result.scalars.return_value.all.return_value = execute_return or []
    result.scalar_one_or_none.return_value = get_return
    result.scalar.return_value = 0
    session.execute = AsyncMock(return_value=result)
    session.add = MagicMock()
    session.commit = AsyncMock()

    async def _get_db():
        yield session

    return _get_db


@pytest.fixture
def mock_empty_db():
    """DB where every lookup returns None / empty list."""
    override = make_mock_db(get_return=None, execute_return=[])
    app.dependency_overrides[get_db] = override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def http():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
