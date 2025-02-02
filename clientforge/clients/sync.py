"""Synchroneous clientforge base client."""

import logging

from httpx import Client

from clientforge.auth import ForgeAuth
from clientforge.clients.base import BaseClient
from clientforge.models import Response

logger = logging.getLogger(__name__)


class ForgeClient(BaseClient):
    """Base class for synchronous API clients."""

    def __init__(
        self,
        api_url: str,
        auth: ForgeAuth | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        """Initialize the client."""
        super().__init__(
            api_url,
            auth,
            session=Client(),
            headers=headers,
            **kwargs,
        )

    def _make_request(
        self, method: str, endpoint: str, params: dict = None, **kwargs
    ) -> Response:
        """Make a request to the API."""
        url = self._api_url.format(endpoint=endpoint)
        request = self._session.build_request(method, url, params=params, **kwargs)
        logger.debug(f"Making request: {request.method} {request.url}")
        response = self._session.send(request)
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(f"Request failed: {response.content}")
            raise err
        return Response(response.status_code, response.content, response.url)
