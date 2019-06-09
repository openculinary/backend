import pytest


@pytest.fixture
def raw_recipe_hit():
    return {
        "_index": "recipes",
        "_type": "recipe",
        "_id": "random-id",
        "_score": 10.04635,
        "_source": {
            "title": "Test Recipe",
            "ingredients": [
                {"ingredient": "1 unit of test ingredient one"},
                {"ingredient": "two units of test ingredient two"}
            ],
            "image": None,
            "time": 30,
            "url": "http://www.example.com/recipes/test"
        },
        "inner_hits": {"ingredients": {"hits": {"hits": []}}}
    }
