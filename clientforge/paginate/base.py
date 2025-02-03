"""Base pagination class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from typing import TYPE_CHECKING

from jsonpath_ng import JSONPath, parse

from clientforge.models import Response

if TYPE_CHECKING:
    from clientforge.clients import AsyncForgeClient, ForgeClient


class BasePaginator(ABC):
    """Pagination class."""

    def __init__(
        self,
        page_size: int = 100,
        page_size_param: str = "limit",
        path_to_data: str = "$",
        **kwargs,
    ):
        """Initialize the pagination class.

        Parameters
        ----------
            page_size: int
                The number of results to return per page.
            page_size_param: str
                The name of the parameter to set the page size.
            path_to_data: str
                The JSONPath to the data in the response.
            **kwargs
                Additional keyword arguments.
        """
        self._page_size = page_size
        self._page_size_param = page_size_param
        self._path_to_data: JSONPath = parse(path_to_data)

        self._kwargs = kwargs

    @abstractmethod
    def _sync_gen(
        self,
        client: ForgeClient,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> Generator[Response, None, None]:
        """Paginate through the results of a request.

        Parameters
        ----------
            client: BaseClientSubclass
                The API client.
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
                The response from the API.
        """

    @abstractmethod
    def _async_gen(
        self,
        client: AsyncForgeClient,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> AsyncGenerator[Response, None]:
        """Paginate through the results of a request.

        Parameters
        ----------
            client: BaseClientSubclass
                The API client.
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
                The response from the API.
        """
