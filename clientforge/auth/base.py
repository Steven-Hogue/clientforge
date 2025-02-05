"""The base authentication class.

The base authentication class is used to define a method for authenticating with
the API. This class should be subclassed to implement the specific authentication
method.
"""

from httpx import Auth


class BaseAuth(Auth):
    """Authentication class."""
