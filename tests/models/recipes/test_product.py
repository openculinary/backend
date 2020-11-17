from reciperadar.models.recipes.product import Product


def test_chicken_contents():
    product = Product(singular='chicken')

    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_breast_contents():
    product = Product(singular='chicken breast')

    assert 'chicken breast' in product.contents
    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_exclusion_contents():
    exclusions = ['broth', 'bouillon', 'soup']

    for exclusion in exclusions:
        product = Product(singular=f'chicken {exclusion}')

        assert f'chicken {exclusion}' in product.contents
        assert 'chicken' not in product.contents

        # TODO: identify meat-derived products
        # assert 'meat' in contents


def test_contents_singularization():
    product = Product(singular='mushroom')

    assert 'mushroom' in product.contents
    assert 'mushrooms' not in product.contents
