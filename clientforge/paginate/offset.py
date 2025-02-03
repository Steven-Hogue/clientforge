"""Offset paginator for paginating through results with an offset parameter."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from typing import TYPE_CHECKING

from jsonpath_ng import JSONPath, parse

from clientforge.exceptions import JSONPathNotFoundError
from clientforge.models import Response
from clientforge.paginate.base import BasePaginator

if TYPE_CHECKING:
    from clientforge.clients import AsyncForgeClient, ForgeClient


class OffsetPaginator(BasePaginator):
    """Offset paginator."""

    def __init__(
        self,
        page_size: int = 100,
        page_size_param: str = "limit",
        path_to_data: str = "$",
        page_offset_param: str = "offset",
        path_to_total: str | None = None,
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
            path_to_total: str, optional
                The JSONPath to the total number of results in the response.
            **kwargs
                Additional keyword arguments.
        """
        super().__init__(
            page_size, page_size_param, path_to_data, supports_async=True, **kwargs
        )

        self._page_offset_param = page_offset_param
        self._path_to_total: JSONPath | None = (
            parse(path_to_total) if path_to_total else None
        )

    def _sync_gen(
        self,
        client: ForgeClient,
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

        if not (response_data := self._path_to_data.find(response.json())):
            raise JSONPathNotFoundError("Data path not found in response.")

        if (
            self._path_to_total is not None
        ):  # If we are able to extract the total number of results
            # Extract the total number of results from the response
            response_total = self._path_to_total.find(response.json())
            if len(response_total) == 0:
                raise JSONPathNotFoundError("Total path not found in response.")
            total = response_total[0].value

            if total <= self._page_size:
                return

            # Paginate through the results
            num_pages = total // self._page_size
            for page in range(1, num_pages + 1):
                params[self._page_offset_param] = page * self._page_size
                response = client(method, endpoint, params=params, **kwargs)

                if not self._path_to_data.find(response.json()):
                    raise JSONPathNotFoundError("Data path not found in response.")

                yield response

        else:  # Otherwise we go until the total number of results at path to data is
            #   less than the page size
            data = response_data[0].value

            total_results = len(data)
            while total_results % self._page_size == 0:
                params[self._page_offset_param] = total_results
                response = client(method, endpoint, params=params, **kwargs)

                response_data = self._path_to_data.find(response.json())
                if (
                    len(response_data) == 0
                    or not response_data
                    or len(data := response_data[0].value) == 0
                ):
                    return  # Assume we have reached the end of the results

                yield response

                total_results += len(data)

    async def _async_gen(
        self,
        client: AsyncForgeClient,
        method: str,
        endpoint: str,
        params: dict | None = None,
        **kwargs,
    ) -> AsyncGenerator[Response, None]:
        params = params or {}
        params[self._page_size_param] = self._page_size

        response = await client(method, endpoint, params=params, **kwargs)
        yield response

        if not response.json():
            return

        if not (response_data := self._path_to_data.find(response.json())):
            raise JSONPathNotFoundError("Data path not found in response.")

        if (
            self._path_to_total is not None
        ):  # If we are able to extract the total number of results
            # Extract the total number of results from the response
            response_total = self._path_to_total.find(response.json())
            if len(response_total) == 0:
                raise JSONPathNotFoundError("Total path not found in response.")
            total = response_total[0].value

            if total <= self._page_size:
                return

            # Paginate through the results
            num_pages = total // self._page_size
            for page in range(1, num_pages + 1):
                params[self._page_offset_param] = page * self._page_size
                response = await client(method, endpoint, params=params, **kwargs)

                if not self._path_to_data.find(response.json()):
                    raise JSONPathNotFoundError("Data path not found in response.")

                yield response

        else:  # Otherwise we go until the total number of results at path to data is
            #   less than the page size
            data = response_data[0].value

            total_results = len(data)
            while total_results % self._page_size == 0:
                params[self._page_offset_param] = total_results
                response = await client(method, endpoint, params=params, **kwargs)

                response_data = self._path_to_data.find(response.json())
                if (
                    len(response_data) == 0
                    or not response_data
                    or len(data := response_data[0].value) == 0
                ):
                    return  # Assume we have reached the end of the results

                yield response

                total_results += len(data)
