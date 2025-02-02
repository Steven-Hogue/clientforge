"""Base class for Forge API clients."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING

from httpx import Client

from clientforge.models import Response

if TYPE_CHECKING:
    from clientforge.auth import ForgeAuth
    from clientforge.paginate import ForgePaginator

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Base class for API clients."""

    def __init__(
        self,
        api_url: str,
        session: Client,
        auth: ForgeAuth | None = None,
        paginator: ForgePaginator | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        """Initialize the client.

        Parameters
        ----------
            api_url: str
                The base URL of the API.
            session: Client
                The HTTPX client session.
            auth: ForgeAuth, optional
                The authentication method to use.
            paginator: ForgePaginator, optional
                The paginator to use.
            headers: dict, optional
                The headers to include all requests.
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

        self._paginator = paginator

    def _generate_pages(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> Generator[Response, None, None]:
        """Paginate through the results of a request.

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
        if not self._paginator:
            raise NotImplementedError("This client does not support pagination.")
        return self._paginator(
            client=self,
            method=method,
            endpoint=endpoint,
            params=params,
            **kwargs,
        )

    @abstractmethod
    def __call__(
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
