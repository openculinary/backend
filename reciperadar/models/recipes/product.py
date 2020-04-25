from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    String,
)
from sqlalchemy.dialects import postgresql

from reciperadar.models.base import Storable


class IngredientProduct(Storable):
    __tablename__ = 'ingredient_products'

    fk = ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    product_id = Column(String)
    product = Column(String)
    product_parser = Column(String)
    is_plural = Column(Boolean)
    singular = Column(String)
    plural = Column(String)
    category = Column(String)
    contents = Column(postgresql.ARRAY(String))

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
            'type': 'product',
            'value': self.product,
            'category': self.category,
            'singular': self.singular,
            'plural': self.plural,
            'state': self.state(include),
        }
