"""Base class for Forge API clients."""

import logging
from abc import ABC, abstractmethod

from httpx import Client

from clientforge.auth import ForgeAuth
from clientforge.models import Response

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Base class for API clients."""

    def __init__(
        self,
        api_url: str,
        session: Client,
        auth: ForgeAuth | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        """Initialize the client.

        Parameters
        ----------
            api_url: str
                The base URL of the API.
            **kwargs
                Additional keyword arguments.
        """
        if "{endpoint}" not in api_url:
            raise ValueError(
                "api_url must contain '{endpoint}' to be replaced with the endpoint."
            )

        self._api_url = api_url
        self._session = session
        self._session.auth = auth
        self._session.headers.update(headers or {})

    @abstractmethod
    def _make_request(
        self, method: str, endpoint: str, params: dict | None = None, **kwargs
    ) -> Response:
        """Make a request to the API.

        Parameters
        ----------
            method: str
                The HTTP method to use.
            endpoint: str
                The endpoint to make the request to.
            params: dict
                The parameters to include in the request.
            **kwargs
                Additional keyword arguments to pass to the request.
        """
