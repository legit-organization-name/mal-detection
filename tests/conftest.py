import os
import pytest


@pytest.fixture
def example_json_data():
    return {"name": "John", "age": 30, "city": "New York"}
