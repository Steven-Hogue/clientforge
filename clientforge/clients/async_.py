"""Synchronous Forge API client."""

import logging

import httpx

from clientforge.auth.base import BaseAuth
from clientforge.clients.base import BaseClient
from clientforge.exceptions import HTTPStatusError
from clientforge.models import ForgeModel, Response, Result
from clientforge.paginate.base import BasePaginator

logger = logging.getLogger(__name__)


class AsyncForgeClient(BaseClient[httpx.AsyncClient]):
    """Base class for asynchronous API clients."""

    def __init__(
        self,
        api_url: str,
        auth: BaseAuth | None = None,
        paginator: BasePaginator | None = None,
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

    async def _model_request(
        self,
        method: str,
        endpoint: str,
        model: type[ForgeModel],
        model_key: str | None = None,
        params: dict | None = None,
        top_n: int = 100,
        **kwargs,
    ) -> Result:
        generator = await self._generate_pages(
            method, endpoint, params=params, **kwargs
        )

        results = []
        async for data in generator:
            results.extend(data.to_model(model, model_key))
            if len(results) >= top_n:
                break

        return Result(results[:top_n])

    async def _generate_pages(self, method, endpoint, params=None, **kwargs):
        if self._paginator is None:
            raise ValueError("Paginator is not set.")
        return self._paginator._async_gen(
            self, method, endpoint, params=params, **kwargs
        )

    async def _make_request(
        self, method: str, endpoint: str, params: dict | None = None, **kwargs
    ):
        request = self._build_request(method, endpoint, params=params, **kwargs)
        logger.debug(f"Making request: {request.method} {request.url}")
        response = await self._session.send(request)
        try:
            response.raise_for_status()
        except Exception as err:
            raise HTTPStatusError(
                f"Request failed: {response.content.decode('utf8')}"
            ) from err

        return Response(response.status_code, response.content, response.url)
