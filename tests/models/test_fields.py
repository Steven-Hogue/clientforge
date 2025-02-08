"""Tests for the fields module."""

import pytest

from clientforge.models.fields import (
    Condition,
    ConditionIterable,
    ConditionOperator,
    Field,
    FieldIterable,
    FieldLength,
)


class MockModel:
    """A mock model for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestField:
    """Tests for the Field class."""

    def setup_method(self):
        """Set up the tests."""
        self.field = Field()
        self.field.__set_name__(MockModel, "test_field")

    def test_field_length_lt(self):
        """Tests."""
        condition = self.field.length < 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_LT
        assert condition.value == 5

    def test_field_length_le(self):
        """Tests."""
        condition = self.field.length <= 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_LE
        assert condition.value == 5

    def test_field_length_eq(self):
        """Tests."""
        condition = self.field.length == 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_EQ
        assert condition.value == 5

    def test_field_length_ge(self):
        """Tests."""
        condition = self.field.length >= 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_GE
        assert condition.value == 5

    def test_field_length_gt(self):
        """Tests."""
        condition = self.field.length > 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_GT
        assert condition.value == 5

    def test_field_lt(self):
        """Tests."""
        condition = self.field < 10
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LT
        assert condition.value == 10

    def test_field_le(self):
        """Tests."""
        condition = self.field <= 10
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LE
        assert condition.value == 10

    def test_field_eq(self):
        """Tests."""
        condition = self.field == 10
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.EQ
        assert condition.value == 10

    def test_field_ge(self):
        """Tests."""
        condition = self.field >= 10
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.GE
        assert condition.value == 10

    def test_field_gt(self):
        """Tests."""
        condition = self.field > 10
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.GT
        assert condition.value == 10

    def test_field_hash(self):
        """Tests."""
        assert hash(self.field) == hash("test_field")

    def test_field_str(self):
        """Tests."""
        assert str(self.field) == "Field(MockModel.test_field)"


class TestCondition:
    """Tests for the Condition class."""

    def setup_method(self):
        """Set up the tests."""
        self.field = Field()
        self.field.__set_name__(MockModel, "test_field")

    def test_condition_evaluate_lt(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LT, 10)
        model = MockModel(test_field=5)
        assert condition.evaluate(model) is True

    def test_condition_evaluate_le(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LE, 10)
        model = MockModel(test_field=10)
        assert condition.evaluate(model) is True

    def test_condition_evaluate_eq(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 10)
        model = MockModel(test_field=10)
        assert condition.evaluate(model) is True

    def test_condition_evaluate_ge(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.GE, 10)
        model = MockModel(test_field=10)
        assert condition.evaluate(model) is True

    def test_condition_evaluate_gt(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.GT, 10)
        model = MockModel(test_field=15)
        assert condition.evaluate(model) is True

    def test_condition_evaluate_len_lt(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LEN_LT, 5)
        model = MockModel(test_field=[1, 2, 3])
        assert condition.evaluate(model) is True

    def test_condition_evaluate_len_le(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LEN_LE, 3)
        model = MockModel(test_field=[1, 2, 3])
        assert condition.evaluate(model) is True

    def test_condition_evaluate_len_eq(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LEN_EQ, 3)
        model = MockModel(test_field=[1, 2, 3])
        assert condition.evaluate(model) is True

    def test_condition_evaluate_len_ge(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LEN_GE, 3)
        model = MockModel(test_field=[1, 2, 3])
        assert condition.evaluate(model) is True

    def test_condition_evaluate_len_gt(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.LEN_GT, 2)
        model = MockModel(test_field=[1, 2, 3])
        assert condition.evaluate(model) is True

    def test_condition_evaluate_unknown_operator(self):
        """Tests."""
        condition = Condition(self.field, "unknown", 10)
        model = MockModel(test_field=10)
        with pytest.raises(ValueError):
            condition.evaluate(model)

    def test_condition_str(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 10)
        assert (
            str(condition)
            == "Condition(Field(MockModel.test_field) ConditionOperator.EQ 10)"
        )


class TestFieldLength:
    """Tests for the FieldLength class."""

    def setup_method(self):
        """Set up the tests."""
        self.field = Field()
        self.field.__set_name__(MockModel, "test_field")

    def test_field_length_lt(self):
        """Tests."""
        condition = self.field.length < 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_LT
        assert condition.value == 5

    def test_field_length_le(self):
        """Tests."""
        condition = self.field.length <= 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_LE
        assert condition.value == 5

    def test_field_length_eq(self):
        """Tests."""
        condition = self.field.length == 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_EQ
        assert condition.value == 5

    def test_field_length_ge(self):
        """Tests."""
        condition = self.field.length >= 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_GE
        assert condition.value == 5

    def test_field_length_gt(self):
        """Tests."""
        condition = self.field.length > 5
        assert isinstance(condition, Condition)
        assert condition.operator == ConditionOperator.LEN_GT
        assert condition.value == 5

    def test_field_length_str(self):
        """Tests."""
        field_length = FieldLength(self.field)
        assert str(field_length) == "FieldLength(Field(MockModel.test_field))"


class TestFieldIterable:
    """Tests for the FieldIterable class."""

    def setup_method(self):
        """Set up the tests."""
        self.field = Field()
        self.field.__set_name__(MockModel, "test_field")

    def test_field_iterable_any(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 1)
        iterable_condition = self.field.where.any(condition)
        assert isinstance(iterable_condition, ConditionIterable)
        assert iterable_condition.strict is False

    def test_field_iterable_all(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 1)
        iterable_condition = self.field.where.all(condition)
        assert isinstance(iterable_condition, ConditionIterable)
        assert iterable_condition.strict is True

    def test_field_iterable_str(self):
        """Tests."""
        iterable_condition = FieldIterable(self.field)
        assert str(iterable_condition) == "FieldIterable(Field(MockModel.test_field))"


class TestConditionIterable:
    """Tests for the ConditionIterable class."""

    def setup_method(self):
        """Set up the tests."""
        self.field = Field()
        self.field.__set_name__(MockModel, "test_field")

    def test_condition_iterable_evaluate_any(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 1)
        iterable_condition = ConditionIterable(self.field, condition, False)
        model = MockModel(test_field=[MockModel(test_field=1), MockModel(test_field=2)])
        assert iterable_condition.evaluate(model) is True

    def test_condition_iterable_evaluate_all(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 1)
        iterable_condition = ConditionIterable(self.field, condition, True)
        model = MockModel(test_field=[MockModel(test_field=1), MockModel(test_field=1)])
        assert iterable_condition.evaluate(model) is True

    def test_condition_iterable_str(self):
        """Tests."""
        condition = Condition(self.field, ConditionOperator.EQ, 1)
        iterable_condition = ConditionIterable(self.field, condition, True)
        assert (
            str(iterable_condition)
            == "ConditionIterable(Condition(Field(MockModel.test_field) ConditionOperator.EQ 1) over Field(MockModel.test_field))"  # noqa: E501
        )
