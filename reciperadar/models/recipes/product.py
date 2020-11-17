from reciperadar import db
from reciperadar.models.base import Storable


class Product(Storable):
    __tablename__ = 'products'
    __table_args__ = (
        db.CheckConstraint("id ~ '^[a-z_]+$'", name='ck_products_id_keyword'),
    )

    parent_fk = db.ForeignKey('products.id', deferrable=True)
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

    nutrition = db.relationship(
        'ProductNutrition',
        backref='product',
        uselist=False,
        passive_deletes='all'
    )
    parent = db.relationship(
        'Product',
        remote_side=[id]
    )

    @property
    def contents(self):
        results = set()
        product = self
        while product:
            results.add(product.singular)
            product = product.parent
        return results


class IngredientProduct(Storable):
    __tablename__ = 'ingredient_products'

    ingredient_fk = db.ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = db.Column(db.String, ingredient_fk, index=True)

    product_fk = db.ForeignKey('products.id', deferrable=True)
    product_id = db.Column(db.String, product_fk, index=True)

    product = db.relationship('Product')

    id = db.Column(db.String, primary_key=True)
    product_parser = db.Column(db.String)
    is_plural = db.Column(db.Boolean)

    STATE_AVAILABLE = 'available'
    STATE_REQUIRED = 'required'

    @staticmethod
    def from_doc(doc):
        id = doc.get('id') or IngredientProduct.generate_id()
        return IngredientProduct(
            id=id,
            product_id=doc.get('product_id'),
            product_parser=doc.get('product_parser'),
            is_plural=doc.get('is_plural'),
        )

    def to_doc(self):
        return {
            **super().to_doc(),
            **self.product.to_doc(),
        }

    def state(self, include):
        states = {
            True: IngredientProduct.STATE_AVAILABLE,
            False: IngredientProduct.STATE_REQUIRED,
        }
        available = bool(set(self.contents or []) & set(include or []))
        return states[available]
