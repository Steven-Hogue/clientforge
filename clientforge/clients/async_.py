"""Synchronous Forge API client."""

import logging

from httpx import AsyncClient

from clientforge.auth import ForgeAuth
from clientforge.clients.base import BaseClient
from clientforge.models import Response
from clientforge.paginate import ForgePaginator

logger = logging.getLogger(__name__)


class AsyncForgeClient(BaseClient[AsyncClient]):
    """Base class for asynchronous API clients."""

    def __init__(
        self,
        api_url: str,
        auth: ForgeAuth | None = None,
        paginator: ForgePaginator | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        super().__init__(
            api_url,
            auth=auth,
            paginator=paginator,
            headers=headers,
            **kwargs,
        )

    def _generate_pages(self, method, endpoint, params=None, **kwargs):
        if self._paginator is None:
            raise ValueError("Paginator is not set.")
        return self._paginator._async_gen(
            self, method, endpoint, params=params, **kwargs
        )

    async def _make_request(
        self, method: str, endpoint: str, params: dict | None = None, **kwargs
    ) -> Response:
        url = self._api_url.format(endpoint=endpoint)
        request = self._session.build_request(method, url, params=params, **kwargs)
        logger.debug(f"Making request: {request.method} {request.url}")
        response = await self._session.send(request)
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(f"Request failed: {response.content.decode('utf8')}")
            raise err
        return Response(response.status_code, response.content, response.url)
