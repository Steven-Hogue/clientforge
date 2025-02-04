"""Tests for the authentication module."""

import pytest
from pytest_httpx import HTTPXMock

from clientforge.auth import ClientCredentialsOAuth2Auth
from clientforge.clients import ForgeClient
from clientforge.exceptions import OAuth2Error


def test_client_credentials_oauth2_auth(httpx_mock: HTTPXMock):
    """Test the ClientCredentialsOAuth2Auth class."""
    httpx_mock.add_response(
        url="https://example.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    auth = ClientCredentialsOAuth2Auth(
        "https://example.com/token",
        client_id="client_id",
        client_secret="client_secret",
        scopes=["scope1", "scope2"],
    )

    assert auth._get_token() == "token"
    assert auth._token == "token"
    assert auth._token_expire_time is not None


def test_client_credentials_oauth2_auth_token_expired(httpx_mock: HTTPXMock):
    """Test the ClientCredentialsOAuth2Auth class when the token is expired."""
    httpx_mock.add_response(
        url="https://example.com/token",
        json={"access_token": "token", "expires_in": 0},
    )

    auth = ClientCredentialsOAuth2Auth(
        "https://example.com/token",
        client_id="client_id",
        client_secret="client_secret",
        scopes=["scope1", "scope2"],
    )

    assert auth._get_token() == "token"
    assert auth._token == "token"

    httpx_mock.add_response(
        url="https://example.com/token",
        json={"access_token": "new_token", "expires_in": 3600},
    )

    assert auth._get_token() == "new_token"
    assert auth._token == "new_token"


def test_client_credentials_oauth2_auth_response_bearer(httpx_mock: HTTPXMock):
    """Test the ClientCredentialsOAuth2Auth class when the response is not OK."""

    class DummyClient(ForgeClient):
        """Dummy client."""

        def __init__(self, base_url: str):
            """Initialize the dummy client."""
            super().__init__(
                base_url,
                auth=ClientCredentialsOAuth2Auth(
                    "https://example.com/token",
                    client_id="client_id",
                    client_secret="client_secret",
                    scopes=["scope1", "scope2"],
                ),
            )

    httpx_mock.add_response(
        url="https://example.com/",
        status_code=200,
        json={},
    )

    httpx_mock.add_response(
        url="https://example.com/token",
        status_code=200,
        json={"access_token": "token", "expires_in": 0, "token_type": "Bearer"},
    )

    client = DummyClient("https://example.com/{endpoint}")
    request = client._build_request("GET", "")
    response = client._session.send(request)

    response.headers["Authorization"] = "Bearer token"


def test_client_credentials_oauth2_auth_response_other(httpx_mock: HTTPXMock):
    """Test the ClientCredentialsOAuth2Auth class when the response is not OK."""

    class DummyClient(ForgeClient):
        """Dummy client."""

        def __init__(self, base_url: str):
            """Initialize the dummy client."""
            super().__init__(
                base_url,
                auth=ClientCredentialsOAuth2Auth(
                    "https://example.com/token",
                    client_id="client_id",
                    client_secret="client_secret",
                    scopes=["scope1", "scope2"],
                ),
            )

    httpx_mock.add_response(
        url="https://example.com/",
        status_code=200,
        json={},
    )

    httpx_mock.add_response(
        url="https://example.com/token",
        status_code=200,
        json={"access_token": "token", "expires_in": 0, "token_type": "Other"},
    )

    client = DummyClient("https://example.com/{endpoint}")
    request = client._build_request("GET", "")
    response = client._session.send(request)

    response.headers["Authorization"] = "Other token"


def test_client_credentials_oauth2_auth_response_no_token_no_expiration(
    httpx_mock: HTTPXMock,
):
    """Test ClientCredentialsOAuth2Auth response missing token or expiration time."""

    class DummyClient(ForgeClient):
        """Dummy client."""

        def __init__(self, base_url: str):
            """Initialize the dummy client."""
            super().__init__(
                base_url,
                auth=ClientCredentialsOAuth2Auth(
                    "https://example.com/token",
                    client_id="client_id",
                    client_secret="client_secret",
                    scopes=["scope1", "scope2"],
                ),
            )

    client = DummyClient("https://example.com/{endpoint}")
    request = client._build_request("GET", "")
    httpx_mock.add_response(
        url="https://example.com/token",
        status_code=200,
        json={"expires_in": 0},
    )

    with pytest.raises(OAuth2Error):
        client._session.send(request)

    httpx_mock.add_response(
        url="https://example.com/token",
        status_code=200,
        json={"access_token": "token"},
    )

    with pytest.raises(OAuth2Error):
        client._session.send(request)


def test_client_credentials_oauth2_auth_response_token_none_expiration_none(
    httpx_mock: HTTPXMock,
):
    """Test ClientCredentialsOAuth2Auth response missing token or expiration time."""

    class DummyClient(ForgeClient):
        """Dummy client."""

        def __init__(self, base_url: str):
            """Initialize the dummy client."""
            super().__init__(
                base_url,
                auth=ClientCredentialsOAuth2Auth(
                    "https://example.com/token",
                    client_id="client_id",
                    client_secret="client_secret",
                    scopes=["scope1", "scope2"],
                ),
            )

    client = DummyClient("https://example.com/{endpoint}")
    request = client._build_request("GET", "")
    httpx_mock.add_response(
        url="https://example.com/token",
        status_code=200,
        json={"access_token": "token", "expires_in": None},
    )

    with pytest.raises(OAuth2Error):
        client._session.send(request)

    httpx_mock.add_response(
        url="https://example.com/token",
        status_code=200,
        json={"access_token": None, "expires_in": 0},
    )

    with pytest.raises(OAuth2Error):
        client._session.send(request)
