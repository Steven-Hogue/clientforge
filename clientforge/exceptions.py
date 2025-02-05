"""Exceptions that are raised throughout."""

# API exceptions


class APIError(Exception):
    """Raised when an API error occurs."""


class InvalidJSONResponse(APIError):
    """Raised when the response is not a JSON response."""


class HTTPStatusError(APIError):
    """Raised when the response status code is not a 200."""


class JSONPathNotFoundError(APIError):
    """Raised when the JSONPath does not match any data in the response."""


# Pagination exceptions


class PaginationError(Exception):
    """Raised when an error occurs during pagination."""


class AsyncNotSupported(PaginationError):
    """Raised when an async method is called on a sync pagination method."""


# Auth exceptions


class AuthError(Exception):
    """Raised when an authentication error occurs."""


class OAuth2Error(Exception):
    """Raised when the response does not contain a required field."""
