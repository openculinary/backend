from collections import deque

from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import joinedload

from reciperadar import admin_app, db
from reciperadar.models.recipes.product import Product, ProductName


class ProductAdmin(ModelView):

    list_template = "admin/products.html"

    column_editable_list = [
        "parent",
        "is_kitchen_staple",
        "is_dairy_free",
        "is_gluten_free",
        "is_vegan",
        "is_vegetarian",
    ]

    column_list = [
        "parent_id",
        "singular_names",
        "plural_names",
        "category",
        "is_kitchen_staple",
        "is_dairy_free",
        "is_gluten_free",
        "is_vegan",
        "is_vegetarian",
    ]

    form_columns = [
        "parent",
        "id",
        "category",
        "is_kitchen_staple",
        "is_dairy_free",
        "is_gluten_free",
        "is_vegan",
        "is_vegetarian",
    ]

    inline_models = [
        (ProductName, {"form_columns": ["singular", "plural"]}),
    ]

    page_size = 0

    def __init__(self):
        super().__init__(Product, db.session)

    def get_list(
        self,
        page,
        sort_column,
        sort_desc,
        search,
        filters,
        execute=True,
        page_size=None,
    ):
        results = []
        products = Product.query.options(
            joinedload(Product.children),
            joinedload(Product.names),
        ).order_by(Product.id)
        sources = deque(filter(lambda x: x.parent is None, products))
        while sources:
            product = sources.popleft()
            children = sorted(product.children, key=lambda p: p.id, reverse=True)
            results.append(product)
            sources.extendleft(children)
        return len(results), results

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.id = model.singular_names[0].replace(" ", "_").replace("-", "_")


admin_app.add_view(ProductAdmin())
