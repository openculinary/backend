import pytest

from reciperadar import app, create_db
from reciperadar.models.recipes.product import Product


@pytest.fixture
def client():
    yield app.test_client()


@pytest.fixture
def _db():
    # TODO: Restore db isolation testing after pytest-flask-sqlalchemy
    # introduces support for sqlalchemy 1.4
    pytest.skip()
    return create_db(app)


@pytest.fixture
def products(db_session):
    from reciperadar import db
    db.session.add(Product(
        id='ancestor_of_one',
        singular='ancestor-of-one',
        plural='ancestor-of-ones',
    ))
    db.session.add(Product(
        id='one',
        singular='one',
        plural='ones',
        parent_id='ancestor_of_one',
        is_vegan=True,
        is_vegetarian=True,
    ))
    db.session.add(Product(
        id='two',
        singular='two',
        plural='twos',
        is_gluten_free=False,
        is_vegetarian=True,
    ))
    db.session.commit()


@pytest.fixture
def raw_recipe_hit(products):
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
                        "<mark class='verb action'>place</mark> each "
                        "<mark class='equipment utensil'>skewer</mark> in the "
                        "<mark class='equipment appliance'>oven</mark>"
                    ),
                    "entities": [
                        {
                            "type": "verb",
                            "category": "action",
                            "name": "place",
                        },
                        {
                            "type": "equipment",
                            "category": "utensil",
                            "name": "skewer",
                        },
                        {
                            "type": "equipment",
                            "category": "appliance",
                            "name": "oven",
                        },
                    ]
                }
            ],
            "ingredients": [
                {
                    "index": 0,
                    "description": "1 unit of test ingredient one",
                    "product": {
                        "product_id": "one",
                    },
                    "magnitude": 50,
                    "units": "ml",
                    "nutrition": {
                        "carbohydrates": 0,
                        "carbohydrates_units": "g",
                        "energy": 0,
                        "energy_units": "cal",
                        "fat": 0.01,
                        "fat_units": "g",
                        "fibre": 0.65,
                        "fibre_units": "g",
                        "protein": 0.05,
                        "protein_units": "g"
                    },
                    "relative_density": 0.5
                },
                {
                    "index": 1,
                    "description": "two units of test ingredient two",
                    "product": {
                        "product_id": "two",
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
