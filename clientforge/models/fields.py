"""A module to define the Field and Condition objects for the Results."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clientforge.models.results import ForgeModel


class ConditionOperator(Enum):
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

    def __init__(self, field: Field) -> None:
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

    def __init__(self, field: Field) -> None:
        """Initialize the field iterable.

        Parameters
        ----------
            field: Field
                The field to apply the condition to.
        """
        self.field = field

    def any(self, condition: Condition):
        """Return a condition for any items in the iterable field."""
        return ConditionIterable(self.field, condition, False)

    def all(self, condition: Condition):
        """Return a condition for all items in the iterable field."""
        return ConditionIterable(self.field, condition, True)

    def __str__(self):
        """Return a string representation of the field."""
        return f"FieldIterable({self.field})"


class Field:
    """A class to represent a field in a model."""

    def __init__(self, owner: type[ForgeModel], name: str) -> None:
        """Initialize the field.

        Parameters
        ----------
            owner: type[ForgeModel]
                The model that the field belongs to.
            name: str
                The name of the field.
        """
        self.owner = owner
        self.name = name

    @property
    def length(self):
        """Return a FieldLength object for the field."""
        return FieldLength(self)

    @property
    def where(self):
        """Return a FieldIterable object for the field."""
        return FieldIterable(self)

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

    def __str__(self):
        """Return a string representation of the field."""
        return f"Field({self.owner.__name__}.{self.name})"


class ConditionIterable:
    """A class to represent a condition on an iterable field in a model."""

    def __init__(self, field: Field, condition: Condition, strict: bool) -> None:
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

    def evaluate(self, model: ForgeModel) -> bool:
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

    def evaluate(self, model: ForgeModel) -> bool:
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
