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

    inflector = inflect.engine()

    _category = None
    _contents = None

    @staticmethod
    def from_doc(doc):
        product = doc.get('product')
        is_plural = doc.get('is_plural')
        singular = doc.get('singular')
        plural = doc.get('plural')

        if not singular or not plural:
            singular = IngredientProduct.inflector.singular_noun(product)
            singular = singular or product
            plural = IngredientProduct.inflector.plural_noun(singular)
            is_plural = product == plural

        product_id = doc.get('id') or IngredientProduct.generate_id()
        return IngredientProduct(
            id=product_id,
            product=product,
            product_parser=doc.get('product_parser'),
            is_plural=is_plural,
            singular=singular,
            plural=plural,
            _category=doc.get('category'),
            _contents=doc.get('contents')
        )

    def to_doc(self):
        result = super().to_doc()
        result['category'] = self.category
        result['contents'] = self.contents
        return result

    def to_dict(self, include):
        states = {
            True: IngredientProduct.STATE_AVAILABLE,
            False: IngredientProduct.STATE_REQUIRED,
        }
        available = bool(set(self.contents) & set(include or []))

        return {
            'type': 'product',
            'value': self.product,
            'category': self.category,
            'singular': self.singular,
            'plural': self.plural,
            'state': states[available]
        }

    @property
    def category(self):
        if self._category:
            return self._category

        category_graph = {
            'bread': 'Bakery',
            'dairy': 'Dairy',
            'dry_goods': 'Dry Goods',
            'fruit_and_veg': 'Fruit & Vegetables',
            'egg': 'Dairy',
            'meat': 'Meat',
            'oil_and_vinegar_and_condiments': 'Oil, Vinegar & Condiments',
        }

        for content in self.contents:
            if content in category_graph:
                self._category = category_graph[content]
                return self._category

    @property
    def contents(self):
        if self._contents:
            return self._contents

        content_graph = {
            'baguette': 'bread',
            'bread': 'bread',
            'loaf': 'bread',

            'butter': 'dairy',
            'cheese': 'dairy',
            'milk': 'dairy',
            'yoghurt': 'dairy',
            'yogurt': 'dairy',

            'all-purpose flour': 'dry_goods',
            'baking powder': 'dry_goods',
            'black pepper': 'dry_goods',
            'brown sugar': 'dry_goods',
            'salt': 'dry_goods',
            'salt and pepper': 'dry_goods',
            'sugar': 'dry_goods',
            'vanilla extract': 'dry_goods',
            'white sugar': 'dry_goods',

            'banana': 'fruit_and_veg',
            'berry': 'fruit_and_veg',
            'berries': 'fruit_and_veg',
            'garlic': 'fruit_and_veg',
            'onion': 'fruit_and_veg',
            'tomato': 'fruit_and_veg',

            'bacon': 'meat',
            'beef': 'meat',
            'chicken': 'meat',
            'ham': 'meat',
            'lamb': 'meat',
            'pork': 'meat',
            'sausage': 'meat',
            'steak': 'meat',
            'turkey': 'meat',
            'venison': 'meat',

            'ketchup': 'oil_and_vinegar_and_condiments',
            'oil': 'oil_and_vinegar_and_condiments',
            'soy sauce': 'oil_and_vinegar_and_condiments',
            'vinegar': 'oil_and_vinegar_and_condiments',
        }
        exclusion_graph = {
            'meat': ['stock', 'broth', 'tomato', 'bouillon', 'soup', 'eggs'],
            'bread': ['crumbs'],
            'fruit_and_veg': ['green tomato'],
        }

        contents = {self.singular}
        for content in content_graph:
            if content in self.product.split():
                excluded = False
                for field in [content, content_graph[content]]:
                    for excluded_term in exclusion_graph.get(field, []):
                        excluded = excluded or excluded_term in self.product
                if excluded:
                    continue
                contents.add(content)
                contents.add(content_graph[content])

        self._contents = list(contents)
        return self._contents
