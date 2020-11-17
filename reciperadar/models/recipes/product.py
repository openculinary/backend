from sqlalchemy.dialects import postgresql

from reciperadar import db
from reciperadar.models.base import Storable
from reciperadar.models.recipes.nutrition import ProductNutrition


class Product(Storable):
    __tablename__ = 'products'

    parent_fk = db.ForeignKey('products.id', ondelete='cascade')
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

    @staticmethod
    def from_doc(doc):
        nutrition = doc.get('nutrition')
        return Product(
            id=doc.get('id'),
            parent_id=doc.get('parent_id'),
            singular=doc.get('singular'),
            plural=doc.get('plural'),
            category=doc.get('category'),
            is_kitchen_staple=doc.get('is_kitchen_staple'),
            is_dairy_free=doc.get('is_dairy_free'),
            is_gluten_free=doc.get('is_gluten_free'),
            is_vegan=doc.get('is_vegan'),
            is_vegetarian=doc.get('is_vegetarian'),
            nutrition=ProductNutrition.from_doc(doc['nutrition'])
            if nutrition else None,
        )


class IngredientProduct(Storable):
    __tablename__ = 'ingredient_products'

    ingredient_fk = db.ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = db.Column(db.String, ingredient_fk, index=True)

    product_fk = db.ForeignKey('products.id', deferrable=True)
    product_id = db.Column(db.String, product_fk, index=True)

    id = db.Column(db.String, primary_key=True)
    product = db.Column(db.String)
    product_parser = db.Column(db.String)
    is_plural = db.Column(db.Boolean)
    singular = db.Column(db.String)
    plural = db.Column(db.String)
    category = db.Column(db.String)
    contents = db.Column(postgresql.ARRAY(db.String))
    is_kitchen_staple = db.Column(db.Boolean)
    is_dairy_free = db.Column(db.Boolean)
    is_gluten_free = db.Column(db.Boolean)
    is_vegan = db.Column(db.Boolean)
    is_vegetarian = db.Column(db.Boolean)

    STATE_AVAILABLE = 'available'
    STATE_REQUIRED = 'required'

    @staticmethod
    def from_doc(doc):
        product_id = doc.get('id') or IngredientProduct.generate_id()
        contents = list(set(
            [doc.get('product')] +
            (doc.get('contents') or []) +
            (doc.get('ancestors') or [])
        ))
        return IngredientProduct(
            id=product_id,
            product_id=doc.get('product_id'),
            product=doc.get('product'),
            product_parser=doc.get('product_parser'),
            is_plural=doc.get('is_plural'),
            singular=doc.get('singular'),
            plural=doc.get('plural'),
            category=doc.get('category'),
            contents=contents,
            is_kitchen_staple=doc.get('is_kitchen_staple'),
            is_dairy_free=doc.get('is_dairy_free'),
            is_gluten_free=doc.get('is_gluten_free'),
            is_vegan=doc.get('is_vegan'),
            is_vegetarian=doc.get('is_vegetarian'),
        )

    def state(self, include):
        states = {
            True: IngredientProduct.STATE_AVAILABLE,
            False: IngredientProduct.STATE_REQUIRED,
        }
        available = bool(set(self.contents or []) & set(include or []))
        return states[available]
