"""Authentication modules."""

import logging
import time
from collections.abc import Generator

from httpx import Client, Request, Response
from oauthlib.oauth2 import BackendApplicationClient

from clientforge.auth.base import BaseAuth
from clientforge.exceptions import OAuth2Error

logger = logging.getLogger(__name__)


class ClientCredentialsOAuth2Auth(BaseAuth):
    """OAuth2 authentication class."""

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scopes: list[str] | None = None,
        session: Client | None = None,
        **kwargs,
    ):
        """Initialize the OAuth2 authentication class.

        Parameters
        ----------
            token_url: str
                The token URL.
            client_id: str, optional
                The client ID.
            client_secret: str, optional
                The client secret.
            scopes: list of str, optional
                The scopes.
            session: httpx.Client, optional
                The HTTPX session.
            **kwargs
                Additional keyword arguments.
        """
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self.scopes = scopes or kwargs["scope"] or []

        self._client = BackendApplicationClient(client_id=client_id)

        self._session = session or Client()

        self._kwargs = kwargs

        self._token = None
        self._token_type = "Bearer"
        self._token_expire_time = 0

    def _get_token(self) -> str:
        """Get the token."""
        if self._token is None or time.time() > self._token_expire_time:
            logger.debug(f"Getting a new token from {self._token_url}")
            body = self._client.prepare_request_body(scope=self.scopes, **self._kwargs)
            response = self._session.request(
                method="POST",
                url=self._token_url,
                content=body,
                auth=(self._client_id, self._client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()

            response_json: dict = response.json()

            if (
                "access_token" not in response_json
                or response_json["access_token"] is None
            ):
                raise OAuth2Error("The response does not contain an access token.")
            if "expires_in" not in response_json or response_json["expires_in"] is None:
                raise OAuth2Error("The response does not contain an expiration time.")

            self._token = response_json["access_token"]
            self._token_type = response_json.get("token_type", "Bearer")
            self._token_expire_time = int(time.time()) + int(
                response_json["expires_in"]
            )

        return self._token  # type: ignore # the token cannot be None

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """Authenticate the request.

        Parameters
        ----------
            request: httpx.Request
                The request to authenticate.
        """
        request.headers["Authorization"] = f"{self._token_type} {self._get_token()}"
        yield request
