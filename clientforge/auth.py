"""Authentication modules."""

import logging
import time
from collections.abc import Generator

from httpx import Auth, Client, Request, Response
from oauthlib.oauth2 import BackendApplicationClient

logger = logging.getLogger(__name__)


class ForgeAuth(Auth):
    """Authentication class."""


class ClientCredentialsOAuth2Auth(ForgeAuth):
    """OAuth2 authentication class."""

    def __init__(
        self,
        token_url: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        scopes: list[str] | None = None,
        session: Client | None = None,
        **kwargs,
    ):
        """Initialize the OAuth2 authentication class."""
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self.scopes = scopes or kwargs["scope"] or []

        self._client = BackendApplicationClient(client_id=client_id)

        self._session = session or Client()

        self._kwargs = kwargs

        self._token = None
        self._token_acquired = None
        self._token_expires = None

    def _get_token(self):
        """Get the token."""
        if self._token is None or time.time() > self._token_expires:
            body = self._client.prepare_request_body(scope=self.scopes, **self._kwargs)
            response = self._session.post(
                self._token_url,
                data=body,
                auth=(self._client_id, self._client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            self._token = response.json()["access_token"]
            self._token_acquired = time.time()
            self._token_expires = self._token_acquired + response.json()["expires_in"]

        return self._token

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """Authenticate the request."""
        request.headers["Authorization"] = f"Bearer {self._get_token()}"
        yield request
