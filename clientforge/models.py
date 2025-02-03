"""Models for the clientforge package."""

import json
from typing import TypeVar

from dataclass_wizard import JSONWizard
from httpx import URL

from clientforge.exceptions import InvalidJSONResponse

MODEL = TypeVar("MODEL", bound="type[ForgeModel]")


class ForgeModel(JSONWizard):
    """A base class for all models."""


class Response:
    """A class to represent a response from the server."""

    def __init__(self, status: int, content: bytes, url: URL) -> None:
        """Initialize the response.

        Parameters
        ----------
            status: int
                The status code of the response.
            content: bytes
                The content of the response as bytes.
            url: str
                The URL of the response.
        """
        self.status = status
        self.content = content
        self.url = url

        self._json: dict | list | None = None

    def json(self) -> dict | list | None:
        """Return the JSON content of the response.

        Raises
        ------
            InvalidResponse: If the response is not a valid JSON response.
        """
        try:
            if not self._json:
                self._json = json.loads(self.content)
            return self._json
        except json.JSONDecodeError as err:
            raise InvalidJSONResponse(
                f"Invalid JSON response from {self.url}: {self.content.decode()}"
            ) from err

    def to_model(self, model_class: MODEL, key: str | int | None = None) -> MODEL:
        """Convert the response to a model.

        Parameters
        ----------
            model_class: MODEL
                The model class to convert the response to.

        Returns
        -------
            MODEL
                The model object.
        """
        self_json = self.json()
        if key is not None and isinstance(self_json, dict):
            self_json = self_json[key]
        elif key is not None and isinstance(self_json, list):
            key = int(key)
            self_json = self_json[key]

        if isinstance(self_json, list):
            return model_class.from_list(self_json)
        else:
            return model_class.from_dict(self_json)

    def get(self, key, default=None):
        """Get a value from the JSON content."""
        return self.json().get(key, default)

    def __getitem__(self, key):
        """Get a value from the JSON content."""
        return self.json()[key]
