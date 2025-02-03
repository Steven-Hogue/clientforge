"""Tests for the synchronous api client module."""

import pytest
from pytest_httpx import HTTPXMock

from clientforge.clients import AsyncForgeClient
from clientforge.exceptions import HTTPStatusError
from clientforge.paginate.base import BasePaginator


class DummyPaginator(BasePaginator):
    """Dummy paginator."""

    def _sync_gen(self, client, method, endpoint, params=None, **kwargs):
        raise NotImplementedError

    async def _async_gen(self, client, method, endpoint, params=None, **kwargs):
        yield "response0"
        yield "response1"
        yield "response2"


@pytest.fixture
def client():
    """Return a synchronous client."""
    return AsyncForgeClient("http://example.com/{endpoint}")


@pytest.mark.asyncio
async def test_generate_pages_no_paginator(client: AsyncForgeClient):
    """Test that a ValueError is raised when no paginator is set."""
    with pytest.raises(ValueError):
        await client._generate_pages("GET", "/endpoint")


@pytest.mark.asyncio
async def test_generate_pages_dummy_paginator(client: AsyncForgeClient):
    """Test the generate pages method."""
    client._paginator = DummyPaginator()
    pages = await client._generate_pages("GET", "/endpoint")
    assert [page async for page in pages] == ["response0", "response1", "response2"]


@pytest.mark.asyncio
async def test_make_request(client: AsyncForgeClient, httpx_mock: HTTPXMock):
    """Test the make request method."""
    httpx_mock.add_response(url="http://example.com/endpoint", json={"key": "value"})
    response = await client._make_request("GET", "endpoint")
    assert response.status == 200
    assert response.json() == {"key": "value"}
    assert response.url == "http://example.com/endpoint"


@pytest.mark.asyncio
async def test_make_request_failed(client: AsyncForgeClient, httpx_mock: HTTPXMock):
    """Test the make request method with a failed request."""
    httpx_mock.add_response(url="http://example.com/endpoint", status_code=500)
    with pytest.raises(HTTPStatusError):
        await client._make_request("GET", "endpoint")
