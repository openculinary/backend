from functools import lru_cache

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
    @lru_cache(maxsize=4096)
    def ancestors(self):
        results = set()
        product = self
        while product:
            results.add(product.singular)
            product = product.parent
        return results

    @property
    @lru_cache(maxsize=4096)
    def contents(self):
        # NB: Use singular noun forms to retain query-time compatibility
        content_graph = {
            'baguette': 'bread',
            'bread': 'bread',
            'loaf': 'bread',

            'butter': 'dairy',
            'cheese': 'dairy',
            'milk': 'dairy',
            'yoghurt': 'dairy',
            'yogurt': 'dairy',

            'anchovy': 'seafood',
            'clam': 'seafood',
            'cod': 'seafood',
            'crab': 'seafood',
            'fish': 'seafood',
            'haddock': 'seafood',
            'halibut': 'seafood',
            'lobster': 'seafood',
            'mackerel': 'seafood',
            'mussel': 'seafood',
            'prawn': 'seafood',
            'salmon': 'seafood',
            'sardine': 'seafood',
            'shellfish': 'seafood',
            'shrimp': 'seafood',
            'squid': 'seafood',
            'tuna': 'seafood',

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
        }
        exclusion_graph = {
            'meat': ['stock', 'broth', 'tomato', 'bouillon', 'soup', 'egg'],
            'bread': ['crumb'],
            'fruit_and_veg': ['green tomato'],
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

    def to_doc(self):
        data = super().to_doc()
        data['contents'] = self.contents
        return data


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
