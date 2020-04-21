from pymmh3 import hash_bytes
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.direction import RecipeDirection
from reciperadar.models.recipes.ingredient import RecipeIngredient


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = Column(String, primary_key=True)
    title = Column(String)
    src = Column(String)
    dst = Column(String)
    domain = Column(String)
    image_src = Column(String)
    time = Column(Integer)
    servings = Column(Integer)
    rating = Column(Float)
    ingredients = relationship(
        'RecipeIngredient',
        backref='recipe',
        passive_deletes='all'
    )
    directions = relationship(
        'RecipeDirection',
        backref='recipe',
        passive_deletes='all'
    )

    indexed_at = Column(DateTime)

    @property
    def noun(self):
        return 'recipes'

    @property
    def url(self):
        return f'/#action=view&id={self.id}'

    @property
    def products(self):
        unique_products = {
            ingredient.product.singular: ingredient.product
            for ingredient in self.ingredients
        }
        return list(unique_products.values())

    @property
    def hidden(self):
        for ingredient in self.ingredients:
            if not ingredient.product.singular:
                return True
        return False

    @staticmethod
    def from_doc(doc):
        src_hash = hash_bytes(doc['src']).encode('utf-8')
        recipe_id = doc.get('id') or Recipe.generate_id(src_hash)
        return Recipe(
            id=recipe_id,
            title=doc['title'],
            src=doc['src'],
            dst=doc.get('dst'),  # TODO: Backwards compatibility; update
            domain=doc['domain'],
            image_src=doc.get('image_src'),
            ingredients=[
                RecipeIngredient.from_doc(ingredient)
                for ingredient in doc['ingredients']
                if ingredient['description'].strip()
            ],
            directions=[
                RecipeDirection.from_doc(direction)
                for direction in doc.get('directions') or []
                if direction['description'].strip()
            ],
            servings=doc['servings'],
            time=doc['time'],
            rating=doc['rating']
        )

    def to_dict(self, include=None):
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time,
            'ingredients': [
                ingredient.to_dict(include)
                for ingredient in self.ingredients
            ],
            'directions': [
                direction.to_dict()
                for direction in sorted(self.directions, key=lambda x: x.index)
            ],
            'servings': self.servings,
            'rating': self.rating,
            'src': self.src,
            'dst': self.dst,
            'domain': self.domain,
            'url': self.url,
            'image_url': self.image_path,
        }

    @property
    def image_path(self):
        return f'images/recipes/{self.id}.png'

    @property
    def contents(self):
        contents = set()
        for product in self.products:
            contents |= set(product.contents or [])
        return list(contents)

    def to_doc(self):
        data = super().to_doc()
        data['directions'] = [
            direction.to_doc()
            for direction in self.directions
        ]
        data['ingredients'] = [
            ingredient.to_doc()
            for ingredient in self.ingredients
        ]
        data['contents'] = self.contents
        data['product_count'] = len(self.products)
        data['hidden'] = self.hidden
        data['src'] = self.dst  # TODO: Backwards compatibility; remove
        return data
