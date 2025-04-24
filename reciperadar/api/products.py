import json

from flask import Response, stream_with_context

from reciperadar import app, db
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.product import ProductName


# Custom streaming method
@stream_with_context
def stream(items):
    for item in items:
        line = json.dumps(item, ensure_ascii=False)
        yield f"{line}\n"


@app.route("/products/hierarchy")
def hierarchy():
    products = (
        db.session.query(
            ProductName,
            db.func.count(),
            db.func.sum(RecipeIngredient.product_is_plural.cast(db.Integer)),
        )
        .join(
            RecipeIngredient,
            isouter=True,
        )
        .group_by(
            ProductName,
        )
    )

    def _product_stream():
        for product_name, count, plural_count in products.all():
            plural_count = plural_count or 0
            is_plural = plural_count > count - plural_count
            yield {
                "product": product_name.plural if is_plural else product_name.singular,
                "recipe_count": count,
                "id": product_name.id,
            }

    return Response(stream(_product_stream()), content_type="application/x-ndjson")
