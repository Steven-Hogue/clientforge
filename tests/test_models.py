"""Tests for the models module."""

from dataclasses import dataclass

import pytest
from httpx import URL

from clientforge.exceptions import InvalidJSONResponse
from clientforge.models import ForgeModel, Response


@dataclass
class DummyModelDict(ForgeModel):
    """Dummy model."""

    key: str


def test_response_initialization():
    """Test the initialization of the response."""
    status = 200
    content = b'{"key": "value"}'
    url = URL("http://example.com")
    response = Response(status, content, url)
    assert response.status == status
    assert response.content == content
    assert response.url == url


def test_response_json():
    """Test the JSON method of the response."""
    status = 200
    content = b'{"key": "value"}'
    url = URL("http://example.com")
    response = Response(status, content, url)
    assert response.json() == {"key": "value"}


def test_response_json_invalid():
    """Test the JSON method of the response with invalid JSON."""
    status = 200
    content = b"invalid json"
    url = URL("http://example.com")
    response = Response(status, content, url)
    with pytest.raises(InvalidJSONResponse):
        response.json()


def test_response_to_model():
    """Test the to_model method of the response."""
    status = 200
    content = b'{"key": "value"}'
    url = URL("http://example.com")
    response = Response(status, content, url)
    model = response.to_model(DummyModelDict)
    assert model.key == "value"


def test_response_to_model_key():
    """Test the to_model method of the response with a key."""
    status = 200
    content = b'{"data": {"key": "value"}}'
    url = URL("http://example.com")
    response = Response(status, content, url)
    model = response.to_model(DummyModelDict, key="data")
    assert model.key == "value"


def test_response_to_model_list():
    """Test the to_model method of the response with a list."""
    status = 200
    content = b'[{"key": "value"}]'
    url = URL("http://example.com")
    response = Response(status, content, url)
    model = response.to_model(DummyModelDict)
    assert model[0].key == "value"


def test_response_to_model_list_key():
    """Test the to_model method of the response with a list and a key."""
    status = 200
    content = b'[{"key": "value"}, {"key": "value2"}]'
    url = URL("http://example.com")
    response = Response(status, content, url)
    model = response.to_model(DummyModelDict, key=0)
    model2 = response.to_model(DummyModelDict, key=1)
    assert model.key == "value"
    assert model2.key == "value2"


def test_response_get():
    """Test the get method of the response."""
    status = 200
    content = b'{"key": "value"}'
    url = URL("http://example.com")
    response = Response(status, content, url)
    assert response.get("key") == "value"
    assert response.get("nonexistent_key") is None


def test_response_getitem():
    """Test the getitem method of the response."""
    status = 200
    content = b'{"key": "value"}'
    url = URL("http://example.com")
    response = Response(status, content, url)
    assert response["key"] == "value"
