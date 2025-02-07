"""Models for the results of the API requests.

The ForgeModel is designed to be a base class for all models defined in the
user's code. The Response class is used to represent the response from the
server and provides methods to convert the response to a model or get values
from the JSON content.
"""

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, TypeVar

import httpx
import jsonpath_ng
import jsonpath_ng.ext
from dataclass_wizard import JSONWizard

from clientforge.exceptions import InvalidJSONResponse

MODEL = TypeVar("MODEL", bound="type[ForgeModel]")


class Result(Generic[MODEL]):
    """Wrapper around the models that has filtering capabilities."""

    def __init__(self, model: MODEL | tuple[MODEL]) -> None:
        """Initialize the response data.

        Parameters
        ----------
            model: ForgeModel
                The model class to convert the data to.
        """
        self.model: tuple[MODEL]

        if hasattr(model, "__iter__") and not isinstance(model, str):
            model = tuple(model)
        elif not isinstance(model, tuple):
            model = (model,)

        self.model = model

    def query(self, query: str | jsonpath_ng.JSONPath) -> "Result":
        """Filter the results using a JSONPath query.

        Parameters
        ----------
            query: str
                The JSONPath query to filter the results.

        Returns
        -------
            Results
                The filtered results.

        Examples
        --------
        >>> results.query("$")
        Result(
            Person(name="Alice", age=25, pets=["Fred", "Fido"]),
            Person(name="Bob", age=30, pets=["Rex"]),
        )
        >>> results.query("name")
        Result("Alice", "Bob")
        >>> results.query("pets[?(@ == 'Fred')]")
        Result(["Fred"])
        >>> results.query("pets")
        Result(["Fred", "Fido"], ["Rex"])
        >>> results.query("pets[*]")
        Result("Fred", "Fido", "Rex")
        """
        return Result(
            res.value
            for model in self.model
            for res in (
                jsonpath_ng.ext.parse(query or "$") if isinstance(query, str) else query
            ).find(model)
        )

    def filter(self, **kwargs) -> "Result":
        """Filter the results using keyword arguments.

        Returns
        -------
            Results
                The filtered results.

        Examples
        --------
        >>> results.filter(name="Alice")
        Result(Person(name="Alice", age=25), Person(name="Alice", age=30))
        >>> results.filter(name="Alice", age=25)
        Result(Person(name="Alice", age=25))
        """
        return Result(
            model
            for model in self.model
            if all(getattr(model, key) == value for key, value in kwargs.items())
        )

    def select(self, *keys: str, **kwargs: str) -> list[dict]:
        """Select specific keys from the results.

        Returns
        -------
            list[dict]
                The selected keys from the results.

        Examples
        --------
        >>> results.select("name", "age")
        [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        >>> results.select("id", perspective="images[*].perspective")
        [{"id": 1, "perspective": "front"}, {"id": 2, "perspective": "back"}]
        """
        parsers = {key: jsonpath_ng.ext.parse(key) for key in keys}
        parsers.update(
            {key: jsonpath_ng.ext.parse(value) for key, value in kwargs.items()}
        )

        output = []
        for model in self.model:
            model_output = {}
            for key, parser in parsers.items():
                value = parser.find(model)
                if value:
                    model_output[key] = value[0].value
            output.append(model_output)
        return output

    def one(self) -> MODEL:
        """Return the first result, if there is more than one result raise an error."""
        if len(self.model) != 1:
            raise ValueError(f"Expected one result, got {len(self.model)}")
        return self.model[0]

    def to_list(self) -> list[MODEL]:
        """Return the results as a list."""
        return list(deepcopy(self.model))

    def __getitem__(self, key: int) -> MODEL:
        """Get a value from the results."""
        return self.model[key]

    def __len__(self):
        """Return the length of the results."""
        return len(self.model)

    def __str__(self):
        """Return a string representation of the results."""
        return str(self.model)

    def __repr__(self):
        """Return a string representation of the results."""
        return f"Results{self.model}"


@dataclass
class ForgeModel(JSONWizard, key_case="CAMEL"):  # type: ignore
    """A base class for all models."""

    class _(JSONWizard.Meta):
        v1 = True

    def get(self, key, default=None):
        """Get a value from the model with a default."""
        return getattr(self, key, default)


class Response:
    """A class to represent a response from the server."""

    def __init__(self, status: int, content: bytes, url: httpx.URL) -> None:
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
        if key is not None and isinstance(self_json, list):
            key = int(key)
            self_json = self_json[key]
        elif key is not None and isinstance(self_json, dict):
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
