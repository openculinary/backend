from reciperadar.models.recipes.product import Product, ProductName


def test_chicken_contents():
    chicken = Product(names=[ProductName(singular="chicken")])

    assert "chicken breast" not in chicken.contents
    assert "chicken" in chicken.contents


def test_chicken_breast_contents():
    chicken = Product(names=[ProductName(singular="chicken")])
    chicken_breast = Product(
        names=[ProductName(singular="chicken breast")],
        parent=chicken,
    )

    assert "chicken breast" in chicken_breast.contents
    assert "chicken" in chicken_breast.contents


def test_contents_singularization():
    mushroom = Product(names=[ProductName(singular="mushroom")])

    assert "mushroom" in mushroom.contents
    assert "mushrooms" not in mushroom.contents
