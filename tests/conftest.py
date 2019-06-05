import pytest


@pytest.fixture
def raw_recipe_hit():
    return {
        "_index": "recipes",
        "_type": "recipe",
        "_id": "random-id",
        "_score": 10.04635,
        "_source": {
            "name": "Test Recipe",
            "ingredients": [
                "1 unit of test ingredient one",
                "two units of test ingredient two"
            ],
            "image": None,
            "time": 30,
            "url": "http://www.example.com/recipes/test"
        }
    }
