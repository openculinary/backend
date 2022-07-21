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


def _product_stream(products):
    for product, name, nutrition, count, plural_count in products.all():
        plural_count = plural_count or 0
        is_plural = plural_count > count - plural_count
        result = {
            "product": name.plural if is_plural else name.singular,
            "recipe_count": count,
            "id": product.id,
        }
        if nutrition:
            result["nutrition"] = nutrition.to_doc()
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

    products = _product_stream(products)
    return Response(stream(products), content_type="application/x-ndjson")
