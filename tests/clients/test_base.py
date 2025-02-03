"""Tests for the base client."""

import pytest
from httpx import AsyncClient, Client

from clientforge.clients.base import BaseClient

# General


class ConcClient(BaseClient[Client]):
    """Concrete client."""

    def _generate_pages(self, method, endpoint, params=None, **kwargs):
        pass

    def _make_request(self, method, endpoint, params=None, **kwargs):
        pass


def test_no_endpoint():
    """Test that a ValueError is raised when no endpoint is provided."""
    with pytest.raises(ValueError):
        ConcClient("http://example.com")


def test_no_generic():
    """Test that a ValueError is raised when no generic client is provided."""
    with pytest.raises(ValueError):

        class NoGenericClient(BaseClient):
            def _generate_pages(self, method, endpoint, params=None, **kwargs):
                pass

            def _make_request(self, method, endpoint, params=None, **kwargs):
                pass

        NoGenericClient("http://example.com/{endpoint}")


@pytest.fixture
def client():
    """Return a concrete client."""
    return ConcClient("http://example.com/{endpoint}")


def assert_client(client: ConcClient):
    """Assert that the client is correctly initialized."""
    assert client.url == "http://example.com/"
    assert client._api_url == "http://example.com/{endpoint}"
    assert client._generate_pages("GET", "/endpoint") is None
    assert client._make_request("GET", "/endpoint") is None
    assert isinstance(client._session, Client)


def test_client(client: ConcClient):
    """Test the concrete client."""
    assert_client(client)


def test_context_manager(client: ConcClient):
    """Test the context manager."""
    session1 = client._session
    with client as c:
        assert_client(c)

    assert session1.is_closed is True

    with client as c:
        assert_client(c)
        session2 = c._session

    assert session2.is_closed is True
    assert session1 is not session2


def test_call(client: ConcClient):
    """Test the call method."""
    assert client("GET", "/endpoint") is None

    with client as c:
        assert c("GET", "/endpoint") is None

    assert client("GET", "/endpoint") is None


# Async


class AsyncConcClient(BaseClient[AsyncClient]):
    """Concrete async client."""

    def _generate_pages(self, method, endpoint, params=None, **kwargs):
        pass

    async def _make_request(self, method, endpoint, params=None, **kwargs):
        pass


@pytest.fixture
def async_client():
    """Return a concrete async client."""
    return AsyncConcClient("http://example.com/{endpoint}")


async def async_assert_client(client: AsyncConcClient):
    """Assert that the async client is correctly initialized."""
    assert client.url == "http://example.com/"
    assert client._api_url == "http://example.com/{endpoint}"
    assert client._generate_pages("GET", "/endpoint") is None
    assert await client._make_request("GET", "/endpoint") is None
    assert isinstance(client._session, AsyncClient)


@pytest.mark.asyncio
async def test_async_client(async_client: AsyncConcClient):
    """Test the async client."""
    await async_assert_client(async_client)


@pytest.mark.asyncio
async def test_async_context_manager(async_client: AsyncConcClient):
    """Test the async context manager."""
    session1 = async_client._session
    async with async_client as c:
        await async_assert_client(c)

    assert session1.is_closed is True

    async with async_client as c:
        await async_assert_client(c)
        session2 = c._session

    assert session2.is_closed is True
    assert session1 is not session2
