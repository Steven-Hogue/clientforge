"""The base authentication class.

The base authentication class is used to define a method for authenticating with
the API. This class should be subclassed to implement the specific authentication
method.
"""

import httpx


class BaseAuth(httpx.Auth):
    """Authentication class."""
