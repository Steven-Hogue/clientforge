"""Tests for the paginate module."""

import pytest
from jsonpath_ng.jsonpath import JSONPath
from pytest_httpx import HTTPXMock

from clientforge.clients import AsyncForgeClient, ForgeClient
from clientforge.exceptions import AsyncNotSupported, JSONPathNotFoundError
from clientforge.models import Response
from clientforge.paginate import OffsetPaginator


class DummyClient(ForgeClient):
    """Dummy client."""

    def __init__(self, base_url: str):
        """Initialize the dummy client."""
        super().__init__(base_url)


class DummyAsyncClient(AsyncForgeClient):
    """Dummy async client."""

    def __init__(self, base_url: str):
        """Initialize the dummy client."""
        super().__init__(base_url)


# OffsetPaginator tests


def test_offset_paginator_attr():
    """Test the offset paginator."""
    offset_paginator = OffsetPaginator()
    assert offset_paginator._page_size == 100
    assert offset_paginator._page_size_param == "limit"
    assert isinstance(offset_paginator._path_to_data, JSONPath)
    assert offset_paginator._page_offset_param == "offset"
    assert isinstance(offset_paginator._path_to_total, JSONPath)


def test_offset_paginator_async_gen():
    """Test the async generator."""
    offset_paginator = OffsetPaginator()
    with pytest.raises(AsyncNotSupported):
        offset_paginator._async_gen(None, "GET", "endpoint")


def test_offset_paginator_gen_once(httpx_mock: HTTPXMock):
    """Test the sync generator."""
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3",
        json={"total": 3, "data": [0, 1, 2]},
    )

    client = DummyClient("http://example.com/{endpoint}")
    client._paginator = OffsetPaginator(
        path_to_data="data", path_to_total="total", page_size=3
    )
    pages = list(client._generate_pages("GET", "endpoint"))
    assert isinstance(pages[0], Response)
    assert [page.json() for page in pages] == [
        {"total": 3, "data": [0, 1, 2]},
    ]


def test_offset_paginator_gen_multiple(httpx_mock: HTTPXMock):
    """Test the sync generator."""
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3",
        json={"total": 5, "data": [0, 1, 2]},
    )
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3&offset=3",
        json={"total": 5, "data": [3, 4]},
    )

    client = DummyClient("http://example.com/{endpoint}")
    client._paginator = OffsetPaginator(
        path_to_data="data", path_to_total="total", page_size=3
    )
    pages = list(client._generate_pages("GET", "endpoint"))
    assert isinstance(pages[0], Response)
    assert [page.json() for page in pages] == [
        {"total": 5, "data": [0, 1, 2]},
        {"total": 5, "data": [3, 4]},
    ]


def test_offset_paginator_gen_empty_response(httpx_mock: HTTPXMock):
    """Test the sync generator."""
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3",
        json={},
    )

    client = DummyClient("http://example.com/{endpoint}")
    client._paginator = OffsetPaginator(
        path_to_data="data", path_to_total="total", page_size=3
    )
    pages = list(client._generate_pages("GET", "endpoint"))
    assert isinstance(pages[0], Response)
    assert [page.json() for page in pages] == [{}]


def test_offset_paginator_gen_no_data_path(httpx_mock: HTTPXMock):
    """Test the sync generator."""
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3",
        json={"total": 5, "notdata": [0, 1, 2]},
    )

    client = DummyClient("http://example.com/{endpoint}")
    client._paginator = OffsetPaginator(
        path_to_data="data", path_to_total="total", page_size=3
    )
    with pytest.raises(JSONPathNotFoundError):
        list(client._generate_pages("GET", "endpoint"))


def test_offset_paginator_gen_no_data_path_in_second_response(
    httpx_mock: HTTPXMock,
):
    """Test the sync generator."""
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3",
        json={"total": 5, "data": [0, 1, 2]},
    )
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3&offset=3",
        json={"total": 5, "notdata": [3, 4]},
    )

    client = DummyClient("http://example.com/{endpoint}")
    client._paginator = OffsetPaginator(
        path_to_data="data", path_to_total="total", page_size=3
    )
    with pytest.raises(JSONPathNotFoundError):
        list(client._generate_pages("GET", "endpoint"))


def test_offset_paginator_gen_no_total_path(httpx_mock: HTTPXMock):
    """Test the sync generator."""
    httpx_mock.add_response(
        url="http://example.com/endpoint?limit=3",
        json={"nottotal": 5, "data": [0, 1, 2]},
    )

    client = DummyClient("http://example.com/{endpoint}")
    client._paginator = OffsetPaginator(
        path_to_data="data", path_to_total="total", page_size=3
    )
    with pytest.raises(JSONPathNotFoundError):
        list(client._generate_pages("GET", "endpoint"))
