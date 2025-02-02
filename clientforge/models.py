"""Models for the clientforge application."""

import json
from typing import TypeVar

from dataclass_wizard import JSONWizard

from clientforge.exceptions import InvalidJSONResponse

MODEL = TypeVar("MODEL", bound="BaseModel")


class BaseModel(JSONWizard):
    """A base class for all models."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Response:
    """A class to represent a response from the server."""

    def __init__(self, status: int, content: bytes, url: str):
        """Initialize the response."""
        self.status = status
        self.content = content
        self.url = url

        self._json = None

    def json(self) -> dict | list:
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

    def to_model(self, model_class: MODEL, key: str = None) -> MODEL:
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
        if key:
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
