import json

from flask import Response

from reciperadar import app, db
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.nutrition import ProductNutrition
from reciperadar.models.recipes.product import Product, ProductName


# Custom streaming method
def stream(items):
    for item in items:
        line = json.dumps(item, ensure_ascii=False)
        yield f"{line}\n"


def _product_map(products):
    product_map = {}
    for product, name, nutrition, count, plural_count in products.all():
        product.name = name
        product.nutrition = nutrition
        product.count = count or 0
        product.plural_count = plural_count or 0
        product_map[product.id] = product
    return product_map


def _product_stream(product_map):
    for product in product_map.values():
        is_plural = product.plural_count > product.count - product.plural_count
        result = {
            "product": product.name.plural if is_plural else product.name.singular,
            "recipe_count": product.count,
            "id": product.id,
            "parent_id": product.parent_id,
        }
        if product.nutrition:
            result["nutrition"] = product.nutrition.to_doc()
        yield result


@app.route("/products/hierarchy")
def hierarchy():
    products = (
        db.session.query(
            Product,
            ProductName,
            ProductNutrition,
            db.func.count(),
            db.func.sum(RecipeIngredient.product_is_plural.cast(db.Integer)),
        )
        .join(ProductName)
        .join(ProductNutrition, isouter=True)
        .join(RecipeIngredient, isouter=True)
        .group_by(
            Product,
            ProductName,
            ProductNutrition,
        )
    )

    product_map = _product_map(products)
    products = _product_stream(product_map)
    return Response(stream(products), content_type="application/x-ndjson")
