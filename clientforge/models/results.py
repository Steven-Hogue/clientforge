"""A module for the results of the models."""

from __future__ import annotations

import json
from abc import ABCMeta
from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

import httpx
import jsonpath_ng.ext
from dataclass_wizard import JSONWizard

from clientforge.exceptions import InvalidJSONResponse, ModelCoercionError
from clientforge.models.fields import Field

if TYPE_CHECKING:
    from clientforge.models.fields import Condition

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

    def filter(self, *conditions: Condition) -> Result:
        """Filter the results based on the conditions.

        Parameters
        ----------
            conditions: Condition
                The conditions to filter the results.

        Returns
        -------
            Result
                The filtered results.

        Examples
        --------
        >>> results.filter(Person.name == "Alice")
        Result(
            Person(name="Alice", age=25, pets=["Fred", "Fido"],
                children=[Child(name="Sally")]
            )
        )
        >>> results.filter(Person.age > 25)
        Result(Person(name="Bob", age=30, pets=["Rex"]))
        >>> results.filter(Person.pets.length == 2)
        Result(
            Person(name="Alice", age=25, pets=["Fred", "Fido"],
                children=[Child(name="Sally")]
            )
        )
        >>> results.filter(Person.children.where.all(Child.name == "Sally"))
        Result(
            Person(name="Alice", age=25, pets=["Fred", "Fido"],
                children=[Child(name="Sally")]
            )
        )
        """
        return Result(
            item
            for item in self.model
            if all(cond.evaluate(item) for cond in conditions)
        )

    def query(self, query: str | jsonpath_ng.JSONPath) -> Result:
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


class ForgeModelMeta(JSONWizard.Meta, ABCMeta):
    """Metaclass for the ForgeModel class."""

    def __new__(
        cls: type[ForgeModelMeta],
        name: str,
        bases: tuple[type, ...],
        namespace: dict,
        **kwargs,
    ) -> type[ForgeModel]:
        """Create the new class with the Field attributes."""
        new_cls = super().__new__(cls, name, bases, namespace, **kwargs)
        if new_cls.__dict__.get("__dataclass_params__") is None:
            dataclass(new_cls)

        for field_name in namespace.get("__annotations__", {}):
            setattr(new_cls, field_name, Field(owner=new_cls, name=field_name))

        return new_cls


class ForgeModel(JSONWizard, metaclass=ForgeModelMeta, key_case="CAMEL"):  # type: ignore
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

    def to_model(self, model_class: MODEL, key: str | int | None = None) -> list[MODEL]:
        """Convert the response to a model.

        Parameters
        ----------
            model_class: MODEL
                The model class to convert the response to.

        Returns
        -------
            list[MODEL]
                A list of model objects.
        """
        self_json = self.json()
        if key is not None and isinstance(self_json, list):
            key = int(key)
            self_json = self_json[key]
        elif key is not None and isinstance(self_json, dict):
            self_json = self_json[key]

        try:
            if isinstance(self_json, list):
                return model_class.from_list(self_json)
            else:
                return [model_class.from_dict(self_json)]
        except TypeError as err:
            raise ModelCoercionError(
                "Error converting response to model "
                f"with key {repr(key)}: {self.json()}"
            ) from err

    def get(self, key, default=None):
        """Get a value from the JSON content."""
        return self.json().get(key, default)

    def __getitem__(self, key):
        """Get a value from the JSON content."""
        return self.json()[key]
