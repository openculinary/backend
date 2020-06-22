from sqlalchemy.dialects import postgresql

from reciperadar import db
from reciperadar.models.base import Storable


class IngredientProduct(Storable):
    __tablename__ = 'ingredient_products'

    fk = db.ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    product_id = db.Column(db.String)
    product = db.Column(db.String)
    product_parser = db.Column(db.String)
    is_plural = db.Column(db.Boolean)
    singular = db.Column(db.String)
    plural = db.Column(db.String)
    category = db.Column(db.String)
    contents = db.Column(postgresql.ARRAY(db.String))

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
            contents=contents
        )

    def state(self, include):
        states = {
            True: IngredientProduct.STATE_AVAILABLE,
            False: IngredientProduct.STATE_REQUIRED,
        }
        available = bool(set(self.contents or []) & set(include or []))
        return states[available]

    def to_dict(self, include):
        return {
            'product_id': self.product_id,
            'product': self.product,
            'value': self.product,
            'category': self.category,
            'singular': self.singular,
            'plural': self.plural,
            'state': self.state(include),
        }
