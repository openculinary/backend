import pytest

from reciperadar.models.recipes import IngredientProduct


def product_categories():
    return {
        'olive oil': 'Oil, Vinegar & Condiments',
        'canola oil': 'Oil, Vinegar & Condiments',
        'white wine vinegar': 'Oil, Vinegar & Condiments',
        'ketchup': 'Oil, Vinegar & Condiments',
    }


def test_chicken_contents():
    product = IngredientProduct(
        product='chicken',
        singular='chicken'
    )

    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_breast_contents():
    product = IngredientProduct(
        product='chicken breast',
        singular='chicken breast'
    )

    assert 'chicken breast' in product.contents
    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_exclusion_contents():
    exclusions = ['broth', 'bouillon', 'soup']

    for exclusion in exclusions:
        product = IngredientProduct(
            product=f'chicken {exclusion}',
            singular=f'chicken {exclusion}'
        )

        assert f'chicken {exclusion}' in product.contents
        assert 'chicken' not in product.contents

        # TODO: identify meat-derived products
        # assert 'meat' in contents


@pytest.mark.parametrize('product,category', product_categories().items())
def test_product_categories(product, category):
    product = IngredientProduct(
        product=product,
        singular=product
    )

    assert product.category == category
