"""Quickly create consistent and reliable clients for REST APIs.

This package provides a simple way to create clients for REST APIs.
Currently, it includes the following extensible modules:

Clients:
    - ForgeClient: A synchronous client for interacting with REST APIs.
    - AsyncForgeClient: An asynchronous client for interacting with REST APIs.

Authentication:
    - ClientCredentialsOAuth2Auth: An OAuth2 authentication class for clients.

"""

__all__ = [
    "ClientCredentialsOAuth2Auth",
    "ForgeClient",
    "AsyncForgeClient",
    "ForgeModel",
    "Response",
    "Result",
    "OffsetPaginator",
]

from clientforge.auth import ClientCredentialsOAuth2Auth
from clientforge.clients.async_ import AsyncForgeClient
from clientforge.clients.sync import ForgeClient
from clientforge.models import ForgeModel, Response, Result
from clientforge.paginate import OffsetPaginator
