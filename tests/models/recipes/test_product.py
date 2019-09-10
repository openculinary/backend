from reciperadar.models.recipes import IngredientProduct


def test_chicken_contents():
    product = IngredientProduct(product='chicken')

    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_breast_contents():
    product = IngredientProduct(product='chicken breast')

    assert 'chicken breast' in product.contents
    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_broth_contents():
    product = IngredientProduct(product='chicken broth')

    assert 'chicken broth' in product.contents
    assert 'chicken' not in product.contents

    # TODO: identify meat-derived products
    # assert 'meat' in contents
