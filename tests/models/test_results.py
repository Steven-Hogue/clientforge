"""Tests for the models module."""

import json

import httpx
import pytest

from clientforge.exceptions import InvalidJSONResponse
from clientforge.models.fields import Condition, ConditionOperator
from clientforge.models.results import ForgeModel, Response, Result


class MockModelChild(ForgeModel):
    """A mock model for testing."""

    name: str
    age: int


class MockModel(ForgeModel):
    """A mock model for testing."""

    name: str
    age: int
    pets: list[str] | None = None
    children: list[MockModelChild] | None = None


class MockModelKey(ForgeModel):
    """A mock model for testing with a key."""

    key: str


class TestResult:
    """Tests for the Result class."""

    def setup_method(self):
        """Set up the test."""
        self.model1 = MockModel(
            name="Alice", age=25, pets=["Fred", "Fido"], children=[]
        )
        self.model2 = MockModel(
            name="Bob",
            age=30,
            pets=["Rex"],
            children=[
                MockModelChild(name="Sally", age=5),
                MockModelChild(name="John", age=10),
            ],
        )
        self.result = Result((self.model1, self.model2))

    def test_result_initialization(self):
        """Test the initialization of the result."""
        assert (
            Result(self.model1).model
            == Result((self.model1,)).model
            == Result([self.model1]).model
            == (self.model1,)
        )

    def test_filter(self):
        """Test the filter method of the result."""
        condition = Condition(MockModel.name, ConditionOperator.EQ, "Alice")
        filtered_result = self.result.filter(condition)
        assert len(filtered_result) == 1
        assert filtered_result[0].name == "Alice"

    def test_query(self):
        """Test the query method of the result."""
        queried_result = self.result.query("name")
        assert len(queried_result) == 2
        assert queried_result[0] == "Alice"
        assert queried_result[1] == "Bob"

    def test_select(self):
        """Test the select method of the result."""
        selected_result = self.result.select("name", "age")
        assert len(selected_result) == 2
        assert selected_result[0] == {"name": "Alice", "age": 25}
        assert selected_result[1] == {"name": "Bob", "age": 30}

        selected_result = self.result.select(all_pets="pets[*]")
        assert len(selected_result) == 2
        assert selected_result[0] == {"all_pets": ["Fred", "Fido"]}

        selected_result = self.result.select(all_children="children[*]")
        assert len(selected_result) == 2
        assert selected_result[0] == {"all_children": None}
        assert selected_result[1] == {
            "all_children": [self.model2.children[0], self.model2.children[1]]
        }

        selected_result = self.result.select(all_children="children[*].name")
        assert len(selected_result) == 2
        assert selected_result[0] == {"all_children": None}
        assert selected_result[1] == {"all_children": ["Sally", "John"]}

    def test_one(self):
        """Test the one method of the result."""
        single_result = Result((self.model1,)).one()
        assert single_result.name == "Alice"
        assert single_result.age == 25

    def test_one_error(self):
        """Test the one method of the result with an error."""
        with pytest.raises(ValueError):
            self.result.one()

    def test_to_list(self):
        """Test the to_list method of the result."""
        result_list = self.result.to_list()
        assert len(result_list) == 2
        assert result_list[0].name == "Alice"
        assert result_list[1].name == "Bob"

    def test_getitem(self):
        """Test the getitem method of the result."""
        assert self.result[0].name == "Alice"
        assert self.result[1].name == "Bob"

    def test_len(self):
        """Test the len method of the result."""
        assert len(self.result) == 2

    def test_str(self):
        """Test the string representation of the result."""
        assert str(self.result) == str((self.model1, self.model2))


class TestResponse:
    """Tests for the Response class."""

    def setup_method(self):
        """Set up the test."""
        self.url = httpx.URL("http://example.com")
        self.content = json.dumps({"name": "Alice", "age": 25}).encode()
        self.response = Response(200, self.content, self.url)

    def test_json(self):
        """Test the JSON method of the response."""
        assert self.response.json() == {"name": "Alice", "age": 25}

    def test_to_model(self):
        """Test the to_model method of the response."""
        model = self.response.to_model(MockModel)
        assert len(model) == 1
        assert model[0].name == "Alice"
        assert model[0].age == 25

    def test_get(self):
        """Test the get method of the response."""
        assert self.response.get("name") == "Alice"
        assert self.response.get("nonexistent", "default") == "default"

    def test_getitem(self):
        """Test the getitem method of the response."""
        assert self.response["name"] == "Alice"

    def test_response_initialization(self):
        """Test the initialization of the response."""
        status = 200
        content = b'{"key": "value"}'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        assert response.status == status
        assert response.content == content
        assert response.url == url

    def test_response_json(self):
        """Test the JSON method of the response."""
        status = 200
        content = b'{"key": "value"}'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        assert response.json() == {"key": "value"}

    def test_response_json_invalid(self):
        """Test the JSON method of the response with invalid JSON."""
        status = 200
        content = b"invalid json"
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        with pytest.raises(InvalidJSONResponse):
            response.json()

    def test_response_to_model(self):
        """Test the to_model method of the response."""
        status = 200
        content = b'{"key": "value"}'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        model = response.to_model(MockModelKey)
        assert model[0].key == "value"

    def test_response_to_model_key(self):
        """Test the to_model method of the response with a key."""
        status = 200
        content = b'{"data": {"key": "value"}}'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        model = response.to_model(MockModelKey, key="data")
        assert model[0].key == "value"

    def test_response_to_model_list(self):
        """Test the to_model method of the response with a list."""
        status = 200
        content = b'[{"key": "value"}]'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        model = response.to_model(MockModelKey)
        assert model[0].key == "value"

    def test_response_to_model_list_key(self):
        """Test the to_model method of the response with a list and a key."""
        status = 200
        content = b'[{"key": "value"}, {"key": "value2"}]'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        model = response.to_model(MockModelKey, key=0)
        model2 = response.to_model(MockModelKey, key=1)
        assert model[0].key == "value"
        assert model2[0].key == "value2"

    def test_response_get(self):
        """Test the get method of the response."""
        status = 200
        content = b'{"key": "value"}'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        assert response.get("key") == "value"
        assert response.get("nonexistent_key") is None

    def test_response_getitem(self):
        """Test the getitem method of the response."""
        status = 200
        content = b'{"key": "value"}'
        url = httpx.URL("http://example.com")
        response = Response(status, content, url)
        assert response["key"] == "value"
