"""Models for the results of the API requests.

The ForgeModel is designed to be a base class for all models defined in the
user's code. The Response class is used to represent the response from the
server and provides methods to convert the response to a model or get values
from the JSON content.
"""

import json
from abc import ABCMeta
from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, TypeVar

import httpx
import jsonpath_ng.ext
from dataclass_wizard import JSONWizard

from clientforge.exceptions import InvalidJSONResponse

MODEL = TypeVar("MODEL", bound="type[ForgeModel]")


class ConditionOperator:
    """An enum to represent the operators for a condition."""

    LT = "lt"
    LE = "le"
    EQ = "eq"
    GE = "ge"
    GT = "gt"
    LEN_LT = "len_lt"
    LEN_LE = "len_le"
    LEN_EQ = "len_eq"
    LEN_GE = "len_ge"
    LEN_GT = "len_gt"


class FieldLength:
    """A class to represent an operation on a field in a model."""

    def __init__(self, field: "Field") -> None:
        """Initialize the field length.

        Parameters
        ----------
            field: Field
                The field to apply the condition to.
        """
        self.field = field

    def __lt__(self, other):
        """Return a condition for the length being lt the other value."""
        return Condition(self.field, ConditionOperator.LEN_LT, other)

    def __le__(self, other):
        """Return a condition for the length being lt or equal to the other value."""
        return Condition(self.field, ConditionOperator.LEN_LE, other)

    def __eq__(self, other):
        """Return a condition for the length being equal to the other value."""
        return Condition(self.field, ConditionOperator.LEN_EQ, other)

    def __ge__(self, other):
        """Return a condition for the length being gt or equal to the other value."""
        return Condition(self.field, ConditionOperator.LEN_GE, other)

    def __gt__(self, other):
        """Return a condition for the length being gt the other value."""
        return Condition(self.field, ConditionOperator.LEN_GT, other)

    def __str__(self):
        """Return a string representation of the field."""
        return f"FieldLength({self.field})"


class FieldIterable:
    """A class to represent an iterable field in a model."""

    def __init__(self, field: "Field") -> None:
        """Initialize the field iterable.

        Parameters
        ----------
            field: Field
                The field to apply the condition to.
        """
        self.field = field

    def any(self, condition: "Condition"):
        """Return a condition for any items in the iterable field."""
        return ConditionIterable(self.field, condition, False)

    def all(self, condition: "Condition"):
        """Return a condition for all items in the iterable field."""
        return ConditionIterable(self.field, condition, True)

    def __str__(self):
        """Return a string representation of the field."""
        return f"FieldIterable({self.field})"


class Field:
    """A class to represent a field in a model."""

    @property
    def length(self):
        """Return a FieldLength object for the field."""
        return FieldLength(self)

    @property
    def where(self):
        """Return a FieldIterable object for the field."""
        return FieldIterable(self)

    def __set_name__(self, owner, name) -> None:
        """Set the name of the field and the owner class."""
        self.owner: type[ForgeModel] = owner
        self.name: str = name

    def __lt__(self, other):
        """Return a condition for the field being lt the other value."""
        return Condition(self, ConditionOperator.LT, other)

    def __le__(self, other):
        """Return a condition for the field being lt or equal to the other value."""
        return Condition(self, ConditionOperator.LE, other)

    def __eq__(self, other):
        """Return a condition for the field being equal to the other value."""
        return Condition(self, ConditionOperator.EQ, other)

    def __ge__(self, other):
        """Return a condition for the field being gt or equal to the other value."""
        return Condition(self, ConditionOperator.GE, other)

    def __gt__(self, other):
        """Return a condition for the field being gt the other value."""
        return Condition(self, ConditionOperator.GT, other)

    def __hash__(self):
        """Return a hash of the field name (required for dataclasses)."""
        return hash(self.name)

    def __str__(self):
        """Return a string representation of the field."""
        return f"Field({self.owner.__name__}.{self.name})"


class ConditionIterable:
    """A class to represent a condition on an iterable field in a model."""

    def __init__(self, field: Field, condition: "Condition", strict: bool) -> None:
        """Initialize the condition.

        Parameters
        ----------
            field: Field
                The field to apply the condition to.
            condition: Condition
                The condition to apply to the field.
            strict: bool
                Whether to apply the condition to all or any of the items.
        """
        self.field = field
        self.condition = condition
        self.strict = strict

    def evaluate(self, model: "ForgeModel") -> bool:
        """Evaluate the condition on the model."""
        field_value: list[ForgeModel] = getattr(model, self.field.name)

        if self.strict:
            out = all(self.condition.evaluate(item) for item in field_value)
        else:
            out = any(self.condition.evaluate(item) for item in field_value)

        return out

    def __str__(self):
        """Return a string representation of the condition."""
        return f"ConditionIterable({self.condition} over {self.field})"


class Condition:
    """A class to represent a condition on a model field."""

    def __init__(self, field: Field, operator: ConditionOperator, value) -> None:
        """Initialize the condition.

        Parameters
        ----------
            field: Field
                The field to apply the condition to.
            operator: ConditionOperator
                The operator to apply to the field.
            value: Any
                The value to compare the field to.
        """
        self.field = field
        self.operator = operator
        self.value = value

    def evaluate(self, model: "ForgeModel") -> bool:
        """Evaluate the condition on the model."""
        field_value = getattr(model, self.field.name)

        match self.operator:
            case ConditionOperator.LT:
                return field_value < self.value
            case ConditionOperator.LE:
                return field_value <= self.value
            case ConditionOperator.EQ:
                return field_value == self.value
            case ConditionOperator.GE:
                return field_value >= self.value
            case ConditionOperator.GT:
                return field_value > self.value

            case ConditionOperator.LEN_LT:
                return len(field_value) < self.value
            case ConditionOperator.LEN_LE:
                return len(field_value) <= self.value
            case ConditionOperator.LEN_EQ:
                return len(field_value) == self.value
            case ConditionOperator.LEN_GE:
                return len(field_value) >= self.value
            case ConditionOperator.LEN_GT:
                return len(field_value) > self.value
            case _:
                raise ValueError(f"Unsupported operator: {self.operator}")

    def __str__(self) -> str:
        """Return a string representation of the condition."""
        return f"Condition({self.field} {self.operator} {self.value})"


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

    def filter(self, *conditions: Condition) -> "Result":
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

    def __new__(cls, name, bases, namespace, **kwargs):
        """Create the new class with the Field attributes."""
        new_namespace = {**namespace}
        for field_name in namespace.get("__annotations__", {}):
            new_namespace[field_name] = Field()

        new_cls = super().__new__(cls, name, bases, new_namespace, **kwargs)

        if new_cls.__dict__.get("__dataclass_params__") is None:
            new_cls = dataclass(new_cls)

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
