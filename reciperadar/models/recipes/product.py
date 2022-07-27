from functools import cached_property
from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

from reciperadar import db
from reciperadar.models.base import Storable
from reciperadar.workers.products import update_product_synonyms


class Product(Storable):
    __tablename__ = "products"
    __table_args__ = (
        db.CheckConstraint("id ~ '^[a-z_]+$'", name="ck_products_id_keyword"),
    )

    parent_fk = db.ForeignKey(
        "products.id",
        deferrable=True,
        ondelete="cascade",
        onupdate="cascade",
    )
    parent_id = db.Column(db.String, parent_fk, index=True)

    id = db.Column(db.String, primary_key=True)
    singular = db.Column(db.String)
    plural = db.Column(db.String)
    category = db.Column(db.String)
    is_kitchen_staple = db.Column(db.Boolean)
    is_dairy_free = db.Column(db.Boolean)
    is_gluten_free = db.Column(db.Boolean)
    is_vegan = db.Column(db.Boolean)
    is_vegetarian = db.Column(db.Boolean)

    names = db.relationship(
        "ProductName", uselist=True, passive_deletes="all", backref="product"
    )
    nutrition = db.relationship(
        "ProductNutrition", uselist=False, passive_deletes="all"
    )
    parent = db.relationship(
        "Product", uselist=False, remote_side=[id], backref="children"
    )

    singular_names = association_proxy("names", "singular")
    plural_names = association_proxy("names", "plural")

    def __str__(self):
        return self.id


class ProductName(Storable):
    __tablename__ = "product_names"

    product_fk = db.ForeignKey(
        "products.id",
        deferrable=True,
        ondelete="cascade",
        onupdate="cascade",
    )

    id = db.Column(db.String, primary_key=True)
    product_id = db.Column(db.String, product_fk, index=True)
    singular = db.Column(db.String, index=True)
    plural = db.Column(db.String)

    @cached_property
    def ancestors(self):
        results = set()
        product_name = self
        while True:
            results.add(product_name.singular)
            if product_name.product and product_name.product.parent:
                product_name = product_name.product.parent.names[0]
            else:
                break
        return results

    @cached_property
    def contents(self):
        # TODO: Move this back to the Product model by introducing content tags
        # NB: Use singular noun forms to retain query-time compatibility
        content_graph = {
            "baguette": "bread",
            "bread": "bread",
            "loaf": "bread",
            "butter": "dairy",
            "cheese": "dairy",
            "milk": "dairy",
            "yoghurt": "dairy",
            "yogurt": "dairy",
            "anchovy": "seafood",
            "clam": "seafood",
            "cod": "seafood",
            "crab": "seafood",
            "fish": "seafood",
            "haddock": "seafood",
            "halibut": "seafood",
            "lobster": "seafood",
            "mackerel": "seafood",
            "mussel": "seafood",
            "prawn": "seafood",
            "salmon": "seafood",
            "sardine": "seafood",
            "shellfish": "seafood",
            "shrimp": "seafood",
            "squid": "seafood",
            "tuna": "seafood",
            "bacon": "meat",
            "beef": "meat",
            "chicken": "meat",
            "ham": "meat",
            "lamb": "meat",
            "pork": "meat",
            "sausage": "meat",
            "steak": "meat",
            "turkey": "meat",
            "venison": "meat",
        }
        exclusion_graph = {
            "meat": ["stock", "broth", "tomato", "bouillon", "soup", "egg"],
            "bread": ["crumb"],
            "fruit_and_veg": ["green tomato"],
        }

        contents = self.ancestors
        for content in content_graph:
            if content in self.singular.split():
                excluded = False
                fields = [content, content_graph[content]]
                for field in fields:
                    for excluded_term in exclusion_graph.get(field, []):
                        excluded = excluded or excluded_term in self.singular
                if excluded:
                    continue
                for field in fields:
                    contents.add(field)
        return list(contents)


@event.listens_for(ProductName, "after_insert")
def after_product_name_insert(mapper, connection, target):
    update_product_synonyms.delay()


@event.listens_for(ProductName, "after_update")
def after_product_name_update(mapper, connection, target):
    update_product_synonyms.delay()


@event.listens_for(ProductName, "after_delete")
def after_product_name_delete(mapper, connection, target):
    update_product_synonyms.delay()
