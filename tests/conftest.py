import pytest

from reciperadar import app, create_db


@pytest.fixture
def client():
    yield app.test_client()


@pytest.fixture
def _db():
    return create_db(app)


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
                    "markup": (
                        "<mark class='action'>place</mark> each "
                        "<mark class='equipment utensil'>skewer</mark> in the "
                        "<mark class='equipment appliance'>oven</mark>"
                    )
                }
            ],
            "ingredients": [
                {
                    "index": 0,
                    "description": "1 unit of test ingredient one",
                    "product": {
                        "product": "one",
                        "contents": ["content-of-one"],
                        "ancestors": ["ancestor-of-one"],
                        "is_vegan": True,
                        "is_vegetarian": True
                    },
                    "magnitude": 50,
                    "units": "ml",
                    "nutrition": {
                        "carbohydrates": 0,
                        "energy": 0,
                        "fat": 0.01,
                        "fibre": 0.65,
                        "protein": 0.05
                    },
                    "relative_density": 0.5
                },
                {
                    "index": 1,
                    "description": "two units of test ingredient two",
                    "product": {
                        "product": "two",
                        "is_gluten_free": False,
                        "is_vegetarian": True
                    },
                    "magnitude": 2,
                    "units": "g"
                }
            ],
            "author": "example",
            "image_src": "http://www.example.com/path/image.png?v=123",
            "time": 30,
            "src": "http://www.example.com/recipes/test",
            "dst": "https://www.example.com/recipes/test",
            "domain": "example.com",
            "servings": 2,
            "rating": 4.5
        },
        "inner_hits": {"ingredients": {"hits": {"hits": []}}}
    }
