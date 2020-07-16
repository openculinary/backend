import pytest

from reciperadar import app, create_db


def pytest_configure(config):
    config.addinivalue_line('markers', 'skip_when_transaction_unavailable')


@pytest.fixture
def client():
    yield app.test_client()


@pytest.fixture
def _db():
    return create_db(app)


@pytest.fixture(autouse=True)
def _skip_when_transaction_unavailable(request, _transaction):
    if request.node.get_closest_marker('skip_when_transaction_unavailable'):
        if not _transaction:
            pytest.skip()


@pytest.fixture
def raw_recipe_hit():
    return {
        "_index": "recipes",
        "_type": "recipe",
        "_id": "random-id",
        "_score": 10.04635,
        "_source": {
            "title": "Test Recipe",
            "directions": [
                {
                    "index": 0,
                    "description": "place each skewer in the oven",
                    "appliances": [
                        {
                            "appliance": "oven"
                        }
                    ],
                    "utensils": [
                        {
                            "utensil": "skewer"
                        }
                    ],
                    "vessels": [
                        {
                            "vessel": "casserole dish"
                        }
                    ]
                }
            ],
            "ingredients": [
                {
                    "index": 0,
                    "description": "1 unit of test ingredient one",
                    "product": {
                        "product": "one",
                        "contents": ["content-of-one"],
                        "ancestors": ["ancestor-of-one"]
                    }
                },
                {
                    "index": 1,
                    "description": "two units of test ingredient two",
                    "product": {"product": "two"}
                }
            ],
            "image_src": "http://www.example.com/path/image.png?v=123",
            "time": 30,
            "src": "http://www.example.com/recipes/test",
            "domain": "example.com",
            "servings": 2,
            "rating": 4.5
        },
        "inner_hits": {"ingredients": {"hits": {"hits": []}}}
    }
