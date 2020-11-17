import json

from flask import Response

from reciperadar import app, db
from reciperadar.models.recipes.ingredient import (
    RecipeIngredient,
)
from reciperadar.models.recipes.nutrition import (
    ProductNutrition,
)
from reciperadar.models.recipes.product import (
    IngredientProduct,
    Product,
)
from reciperadar.search.products import ProductSearch


# Custom streaming method
def stream(items):
    for item in items:
        line = json.dumps(item, ensure_ascii=False)
        yield f'{line}\n'


@app.route('/products')
def products():
    products = ProductSearch().products()
    return Response(stream(products), content_type='application/x-ndjson')


def _product_map(products):
    product_map = {}
    for product, nutrition, count, plural_count in products.all():
        product.nutrition = nutrition
        product.count = count or 0
        product.plural_count = plural_count or 0
        product_map[product.id] = product
    return product_map


def _calculate_depth(product_map, product):
    if product.parent_id is None:
        return 0
    parent = product_map[product.parent_id]
    return _calculate_depth(product_map, parent) + 1


def _product_stream(product_map):
    for product in product_map.values():
        depth = _calculate_depth(product_map, product)
        is_plural = product.plural_count > product.count - product.plural_count
        result = {
            'product': product.plural if is_plural else product.singular,
            'recipe_count': product.count,
            'id': product.id,
            'parent_id': product.parent_id,
            'depth': depth,
        }
        if product.nutrition:
            result['nutrition'] = product.nutrition.to_doc()
        yield result


@app.route('/products/hierarchy')
def hierarchy():
    products = (
        db.session.query(
            Product,
            ProductNutrition,
            db.func.count(),
            db.func.sum(IngredientProduct.is_plural.cast(db.Integer)),
        )
        .join(ProductNutrition, isouter=True)
        .join(IngredientProduct, isouter=True)
        .join(RecipeIngredient, isouter=True)
        .group_by(
            Product,
            ProductNutrition,
        )
    )

    product_map = _product_map(products)
    products = _product_stream(product_map)
    return Response(stream(products), content_type='application/x-ndjson')
