"""Base class for the API clients.

The base class for the API clients defines the common methods and properties
that all clients should implement. This class itself should not be used directly,
but should be subclassed to implement the specific API client.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Coroutine, Generator
from typing import TYPE_CHECKING, Generic, TypeVar, get_args, get_origin

import httpx

if TYPE_CHECKING:
    from clientforge.auth.base import BaseAuth
    from clientforge.models import Response
    from clientforge.paginate.base import BasePaginator

logger = logging.getLogger(__name__)

HTTPXClientSubclass = TypeVar("HTTPXClientSubclass", bound=httpx._client.BaseClient)


class BaseClient(ABC, Generic[HTTPXClientSubclass]):
    """Base class for API clients."""

    def __init__(
        self,
        api_url: str,
        auth: BaseAuth | None = None,
        paginator: BasePaginator | None = None,
        headers: dict | None = None,
        session_kwargs: dict | None = None,
        **kwargs,
    ):
        """Initialize the client.

        Parameters
        ----------
            api_url: str
                The base URL of the API.
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
        self._auth = auth
        self._headers = headers or {}
        self._session_kwargs = session_kwargs or {}

        self._paginator = paginator

        self._session: HTTPXClientSubclass = self._new_session()

    def _infer_session_type(self) -> type[HTTPXClientSubclass]:
        """Extract the session type from the generic parameter."""
        for base in self.__class__.__orig_bases__:  # type: ignore
            origin = get_origin(base)
            if origin is None or not issubclass(origin, BaseClient):
                continue
            type_args = get_args(base)
            if type_args:
                session_type = type_args[0]
                if isinstance(session_type, type):
                    return session_type
        raise ValueError(
            "Could not infer session_type. Ensure your subclass specifies "
            "BaseClient[YourSessionSubclass] as the base class."
        )

    def _new_session(self) -> HTTPXClientSubclass:
        """Create a new session."""
        session = self._infer_session_type()(**self._session_kwargs)
        session.auth = self._auth
        session.headers.update(self._headers)
        return session

    @property
    def url(self) -> str:
        """The base URL of the API."""
        return self._api_url.format(endpoint="")

    @abstractmethod
    def _generate_pages(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> (
        Generator[Response, None, None]
        | Coroutine[None, None, AsyncGenerator[Response, None]]
    ):
        """Generate pages of results from the API.

        Parameters
        ----------
            method: str
                The HTTP method to use.
            endpoint: str
                The API endpoint to request.
            params: dict, optional
                The query parameters to send with the request.
            **kwargs
                Additional keyword arguments.

        Yields
        ------
            Response
                The response object.
        """

    def _build_request(
        self, method: str, endpoint: str, params: dict | None = None, **kwargs
    ) -> httpx.Request:
        """Prepare a request to the API.

        Parameters
        ----------
            method: str
                The HTTP method to use.
            endpoint: str
                The API endpoint to request.
            params: dict, optional
                The query parameters to send with the request.
            **kwargs
                Additional keyword arguments.

        Returns
        -------
            Request
                The request object.
        """
        url = self._api_url.format(endpoint=endpoint)
        return self._session.build_request(method, url, params=params, **kwargs)

    @abstractmethod
    def _make_request(
        self, method: str, endpoint: str, params: dict | None = None, **kwargs
    ) -> Response | Coroutine[None, None, Response]:
        """Make a request to the API.

        Parameters
        ----------
            method: str
                The HTTP method to use.
            endpoint: str
                The API endpoint to request.
            params: dict, optional
                The query parameters to send with the request.
            **kwargs
                Additional keyword arguments.

        Returns
        -------
            Response
                The response object.
        """

    def __call__(
        self, method: str, endpoint: str, params: dict | None = None, **kwargs
    ):
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
        if self._session.is_closed:
            self._session = self._new_session()
        return self._make_request(method, endpoint, params=params, **kwargs)

    def __enter__(self):
        """Enter the context manager."""
        if self._session.is_closed:
            self._session = self._new_session()
            self._session.__enter__()
        return self

    def __exit__(self, *args):
        """Exit the context manager."""
        self._session.__exit__(*args)
        return False

    async def __aenter__(self):
        """Enter the async context manager."""
        if self._session.is_closed:
            self._session = self._new_session()
            await self._session.__aenter__()
        return self

    async def __aexit__(self, *args):
        """Exit the async context manager."""
        await self._session.__aexit__(*args)
        return False
