from flask_admin.contrib.sqla import ModelView

from reciperadar import admin_app, db
from reciperadar.models.recipes.product import Product


class ProductAdmin(ModelView):

    list_template = "admin/products.html"

    form_columns = [
        "parent",
        "singular",
        "plural",
        "category",
        "is_kitchen_staple",
        "is_dairy_free",
        "is_gluten_free",
        "is_vegan",
        "is_vegetarian",
    ]

    def __init__(self):
        super().__init__(Product, db.session)

    def on_model_change(self, form, model, is_created):
        model.id = model.singular


admin_app.add_view(ProductAdmin())
