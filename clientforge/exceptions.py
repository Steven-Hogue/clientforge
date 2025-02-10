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


# Model exceptions


class ModelError(Exception):
    """Raised when an error occurs during model conversion."""


class ModelCoercionError(ModelError):
    """Raised when an error occurs during model coercion."""


# Field/condition exceptions


class FieldError(Exception):
    """Raised when an error occurs during field creation."""


class UnknownOperatorError(FieldError):
    """Raised when an unknown operator is used in a condition."""


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
