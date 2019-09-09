import inflect
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    String,
)

from reciperadar.models.base import Storable


class IngredientProduct(Storable):
    __tablename__ = 'ingredient_products'

    fk = ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    product = Column(String)
    product_parser = Column(String)
    is_plural = Column(Boolean)
    singular = Column(String)
    plural = Column(String)

    STATE_AVAILABLE = 'available'
    STATE_REQUIRED = 'required'

    state = None

    inflector = inflect.engine()

    @staticmethod
    def from_doc(doc, matches=None):
        product = doc.get('product')
        product_parser = doc.get('product_parser')

        is_plural = doc.get('is_plural')
        singular = doc.get('singular')
        plural = doc.get('plural')

        if not singular or not plural:
            singular = IngredientProduct.inflector.singular_noun(product)
            singular = singular or product
            plural = IngredientProduct.inflector.plural_noun(singular)
            is_plural = product == plural

        matches = matches or []
        states = {
            True: IngredientProduct.STATE_AVAILABLE,
            False: IngredientProduct.STATE_REQUIRED,
        }
        state = states[singular in matches or plural in matches]

        product_id = doc.get('id') or IngredientProduct.generate_id()
        return IngredientProduct(
            id=product_id,
            product=product,
            product_parser=product_parser,
            is_plural=is_plural,
            singular=singular,
            plural=plural,
            state=state
        )
