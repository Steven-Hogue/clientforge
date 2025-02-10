"""Tests for the ronous api client module."""

import pytest
from pytest_httpx import HTTPXMock

from clientforge.clients import ForgeClient
from clientforge.exceptions import HTTPStatusError
from clientforge.models import ForgeModel, Response, Result
from clientforge.paginate.base import BasePaginator


class DummyPaginator(BasePaginator):
    """Dummy paginator."""

    def _async_gen(self, client, method, endpoint, params=None, **kwargs):
        raise NotImplementedError

    def _sync_gen(self, client, method, endpoint, params=None, **kwargs):
        yield Response(200, b'{"text":"response0"}', "http://example.com/endpoint")
        yield Response(200, b'{"text":"response1"}', "http://example.com/endpoint")
        yield Response(200, b'{"text":"response2"}', "http://example.com/endpoint")


class MockModel(ForgeModel):
    """A mock model."""

    text: str


class TestForgeClient:
    """Tests for the ForgeClient class."""

    def setup_method(self):
        """Set up the tests."""
        self.client = ForgeClient("http://example.com/{endpoint}")
        self.client._paginator = DummyPaginator()

    def test_init(self):
        """Test the initialization of the client."""
        assert self.client._api_url == "http://example.com/{endpoint}"
        assert self.client._auth is None
        assert isinstance(self.client._paginator, DummyPaginator)
        assert self.client._headers == {}

    def test_model_request(self):
        """Test the model request method."""
        result = self.client._model_request("GET", "/endpoint", MockModel, top_n=2)
        assert isinstance(result, Result)
        assert len(result) == 2
        assert result[0].text == "response0"
        assert result[1].text == "response1"

    def test_generate_pages_no_paginator(self):
        """Test that a ValueError is raised when no paginator is set."""
        self.client._paginator = None
        with pytest.raises(ValueError):
            self.client._generate_pages("GET", "/endpoint")

    def test_generate_pages_dummy_paginator(self):
        """Test the generate pages method."""
        pages = self.client._generate_pages("GET", "/endpoint")
        pages = [page for page in pages]
        assert len(pages) == 3
        assert pages[0].status == 200
        assert pages[0].json() == {"text": "response0"}
        assert pages[0].url == "http://example.com/endpoint"
        assert pages[2].status == 200
        assert pages[2].json() == {"text": "response2"}
        assert pages[2].url == "http://example.com/endpoint"

    def test_make_request(self, httpx_mock: HTTPXMock):
        """Test the make request method."""
        httpx_mock.add_response(
            url="http://example.com/endpoint", json={"key": "value"}
        )
        response = self.client._make_request("GET", "endpoint")
        assert response.status == 200
        assert response.json() == {"key": "value"}
        assert response.url == "http://example.com/endpoint"

    def test_make_request_failed(self, httpx_mock: HTTPXMock):
        """Test the make request method with a failed request."""
        httpx_mock.add_response(url="http://example.com/endpoint", status_code=500)
        with pytest.raises(HTTPStatusError):
            self.client._make_request("GET", "endpoint")
