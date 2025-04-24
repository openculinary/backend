from functools import cached_property
from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

from reciperadar import db
from reciperadar.models.base import Storable
from reciperadar.workers.products import update_product_synonyms


class Product(Storable):
    __tablename__ = "products"

    parent_fk = db.ForeignKey(
        "products.id",
        deferrable=True,
        ondelete="cascade",
        onupdate="cascade",
    )
    parent_id = db.Column(db.String, parent_fk, index=True)

    id = db.Column(db.String, primary_key=True)
    wdqid = db.Column(db.String)
    category = db.Column(db.String)
    is_kitchen_staple = db.Column(db.Boolean)
    is_dairy_free = db.Column(db.Boolean)
    is_gluten_free = db.Column(db.Boolean)
    is_vegan = db.Column(db.Boolean)
    is_vegetarian = db.Column(db.Boolean)

    names = db.relationship(
        "ProductName", uselist=True, passive_deletes="all", backref="product"
    )
    parent = db.relationship(
        "Product", uselist=False, remote_side=[id], backref="children"
    )

    singular_names = association_proxy("names", "singular")
    plural_names = association_proxy("names", "plural")

    def __str__(self):
        return self.id

    @cached_property
    def contents(self):
        contents = set()
        for name in self.names:
            contents |= set(name.contents or [])
        return sorted(contents)

    def to_doc(self):
        data = super().to_doc()
        data["contents"] = self.contents
        return data


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
        product = self.product
        while product:
            yield product
            product = product.parent

    @cached_property
    def contents(self):
        results = set()
        for product in self.ancestors:
            for product_name in product.names:
                results.add(product_name.singular)
        return results


@event.listens_for(ProductName, "after_insert")
def after_product_name_insert(mapper, connection, target):
    update_product_synonyms.delay()


@event.listens_for(ProductName, "after_update")
def after_product_name_update(mapper, connection, target):
    update_product_synonyms.delay()


@event.listens_for(ProductName, "after_delete")
def after_product_name_delete(mapper, connection, target):
    update_product_synonyms.delay()
