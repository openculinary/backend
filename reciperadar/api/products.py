import json

from flask import Response, stream_with_context

from reciperadar import app, db
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.nutrition import ProductNutrition
from reciperadar.models.recipes.product import ProductName


# Custom streaming method
def stream(items):
    for item in items:
        line = json.dumps(item, ensure_ascii=False)
        yield f"{line}\n"


@app.route("/products/hierarchy")
def hierarchy():
    products = (
        db.session.query(
            ProductName,
            ProductNutrition,
            db.func.count(),
            db.func.sum(RecipeIngredient.product_is_plural.cast(db.Integer)),
        )
        .join(
            ProductNutrition,
            ProductNutrition.product_id == ProductName.product_id,
            isouter=True,
        )
        .join(
            RecipeIngredient,
            isouter=True,
        )
        .group_by(
            ProductName,
            ProductNutrition,
        )
    )

    def _product_stream():
        for product_name, nutrition, count, plural_count in products.all():
            plural_count = plural_count or 0
            is_plural = plural_count > count - plural_count
            result = {
                "product": product_name.plural if is_plural else product_name.singular,
                "recipe_count": count,
                "id": product_name.id,
            }
            if nutrition:
                result["nutrition"] = nutrition.to_doc()
            yield result

    return Response(stream_with_context(stream(_product_stream())), content_type="application/x-ndjson")
