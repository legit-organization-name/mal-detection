import os

from src.util import read_json


def test_json_util(data_dir, example_json_data):
    filepath = os.path.join(data_dir, "example_data.json")
    assert os.path.isfile(filepath)

    data = read_json(filepath)

    assert example_json_data == data
