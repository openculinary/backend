import pytest

from sqlalchemy import event

from reciperadar import app, db
from reciperadar.models.recipes.product import Product, ProductName


@pytest.fixture(autouse=True)
def celery_broker():
    from reciperadar.workers.broker import celery

    celery.conf.update({"broker_url": "memory://"})


@pytest.fixture
def client():
    yield app.test_client()


@pytest.fixture
def connection():
    return db.engine.connect()


@pytest.fixture
def db_session(connection):
    """
    Sourced from https://github.com/jeancochrane/pytest-flask-sqlalchemy/issues/46#issuecomment-829694672  # noqa
    """
    db_session_options = {"bind": connection, "binds": {}}

    transaction = connection.begin()
    db.session = db.create_scoped_session(options=db_session_options)
    db.session.begin_nested()

    # for handling tests that actually call "session.rollback()"
    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    @event.listens_for(db.session, "after_transaction_end")
    def restart_savepoint(session, transaction_in):
        if transaction_in.nested and not transaction_in._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield db.session

    db.session.close()
    transaction.rollback()


@pytest.fixture
def products(db_session):
    from reciperadar import db

    db.session.add(
        Product(
            id="ancestor_of_one",
        )
    )
    db.session.add(
        ProductName(
            id="ancestor_of_one",
            product_id="ancestor_of_one",
            singular="ancestor-of-one",
            plural="ancestor-of-ones",
        )
    )
    db.session.add(
        Product(
            id="one",
            parent_id="ancestor_of_one",
            is_vegan=True,
            is_vegetarian=True,
        )
    )
    db.session.add(
        ProductName(
            id="one",
            product_id="one",
            singular="one",
            plural="ones",
        )
    )
    db.session.add(
        Product(
            id="two",
            is_gluten_free=False,
            is_vegetarian=True,
        )
    )
    db.session.add(
        ProductName(
            id="two",
            product_id="two",
            singular="two",
            plural="twos",
        )
    )
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
                    ],
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
                        "protein_units": "g",
                    },
                    "relative_density": 0.5,
                },
                {
                    "index": 1,
                    "description": "two units of test ingredient two",
                    "product": {
                        "product_id": "two",
                    },
                    "magnitude": 2,
                    "units": "g",
                },
            ],
            "author": "example",
            "image_src": "http://www.example.com/path/image.png?v=123",
            "time": 30,
            "src": "http://www.example.com/recipes/test",
            "dst": "https://www.example.com/recipes/test",
            "domain": "example.com",
            "servings": 2,
            "rating": 4.5,
        },
        "inner_hits": {"ingredients": {"hits": {"hits": []}}},
    }
