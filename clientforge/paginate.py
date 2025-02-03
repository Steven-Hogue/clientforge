"""Pagination modules."""

from abc import ABC, abstractmethod
from collections.abc import Coroutine, Generator
from typing import TypeVar

from jsonpath_ng import JSONPath, parse

from clientforge.clients.base import BaseClient
from clientforge.exceptions import AsyncNotSupported, JSONPathNotFoundError
from clientforge.models import Response

BaseClientSubclass = TypeVar("BaseClientSubclass", bound=BaseClient)


class ForgePaginator(ABC):
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
        client: BaseClientSubclass,
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
        client: BaseClientSubclass,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> Generator[Coroutine[None, None, Response], None, None]:
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


class OffsetPaginator(ForgePaginator):
    """Offset paginator."""

    def __init__(
        self,
        page_size: int = 100,
        page_size_param: str = "limit",
        path_to_data: str = "$",
        page_offset_param: str = "offset",
        path_to_total: str = "total",
        **kwargs,
    ):
        """Initialize the offset paginator.

        Parameters
        ----------
            page_size: int
                The number of results to return per page.
            page_size_param: str
                The name of the parameter to set the page size.
            path_to_data: str
                The JSONPath to the data in the response.
            page_offset_param: str
                The name of the parameter to set the page offset.
            path_to_total: str
                The JSONPath to the total number of results in the response.
            **kwargs
                Additional keyword arguments.
        """
        super().__init__(
            page_size, page_size_param, path_to_data, supports_async=True, **kwargs
        )

        self._page_offset_param = page_offset_param
        self._path_to_total: JSONPath = parse(path_to_total)

    def _sync_gen(
        self,
        client: BaseClientSubclass,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> Generator[Response, None, None]:
        params = params or {}
        params[self._page_size_param] = self._page_size

        response = client(method, endpoint, params=params, **kwargs)
        yield response

        if not response.json():
            return

        # Extract the data from the response
        response_data = self._path_to_data.find(response.json())
        if len(response_data) == 0:
            raise JSONPathNotFoundError("Data path not found in response.")
        data = response_data[0].value

        # Extract the total number of results from the response
        response_total = self._path_to_total.find(response.json())
        if len(response_total) == 0:
            raise JSONPathNotFoundError("Total path not found in response.")
        total = response_total[0].value

        # Paginate through the results
        total_results = len(data)
        while total_results < total:
            params[self._page_offset_param] = total_results
            response = client(method, endpoint, params=params, **kwargs)

            yield response

            response_data = self._path_to_data.find(response.json())
            if len(response_data) == 0:
                raise JSONPathNotFoundError("Data path not found in response.")
            data = response_data[0].value
            total_results += len(data)

    def _async_gen(
        self,
        client: BaseClientSubclass,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ):
        raise AsyncNotSupported("OffsetPaginator does not support async pagination.")
