import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@pytest.fixture
def data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return DATA_DIR


@pytest.fixture
def example_json_data():
    return {
        "name": "John",
        "age": 30,
        "city": "New York"
    }