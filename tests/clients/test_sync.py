"""Tests for the synchronous api client module."""

import pytest
from pytest_httpx import HTTPXMock

from clientforge.clients import ForgeClient
from clientforge.exceptions import HTTPStatusError
from clientforge.paginate.base import BasePaginator


class DummyPaginator(BasePaginator):
    """Dummy paginator."""

    def _sync_gen(self, client, method, endpoint, params=None, **kwargs):
        yield "response0"
        yield "response1"
        yield "response2"

    async def _async_gen(self, client, method, endpoint, params=None, **kwargs):
        raise NotImplementedError


@pytest.fixture
def client():
    """Return a synchronous client."""
    return ForgeClient("http://example.com/{endpoint}")


def test_generate_pages_no_paginator(client: ForgeClient):
    """Test that a ValueError is raised when no paginator is set."""
    with pytest.raises(ValueError):
        client._generate_pages("GET", "/endpoint")


def test_generate_pages_dummy_paginator(client: ForgeClient):
    """Test the generate pages method."""
    client._paginator = DummyPaginator()
    pages = client._generate_pages("GET", "/endpoint")
    assert list(pages) == ["response0", "response1", "response2"]


def test_make_request(client: ForgeClient, httpx_mock: HTTPXMock):
    """Test the make request method."""
    httpx_mock.add_response(url="http://example.com/endpoint", json={"key": "value"})
    response = client._make_request("GET", "endpoint")
    assert response.status == 200
    assert response.json() == {"key": "value"}
    assert response.url == "http://example.com/endpoint"


def test_make_request_failed(client: ForgeClient, httpx_mock: HTTPXMock):
    """Test the make request method with a failed request."""
    httpx_mock.add_response(url="http://example.com/endpoint", status_code=500)
    with pytest.raises(HTTPStatusError):
        client._make_request("GET", "endpoint")
