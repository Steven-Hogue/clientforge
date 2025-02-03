"""Exceptions that are raised by the clientforge package."""


class InvalidJSONResponse(Exception):
    """Raised when the response is not a JSON response."""


class HTTPStatusError(Exception):
    """Raised when the response status code is not a 200."""


class JSONPathNotFoundError(Exception):
    """Raised when the JSONPath does not match any data in the response."""


class AsyncNotSupported(Exception):
    """Raised when an async method is called on a sync pagination method."""
