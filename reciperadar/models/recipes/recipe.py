from pymmh3 import hash_bytes

from reciperadar import db
from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.direction import RecipeDirection
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.nutrition import IngredientNutrition
from reciperadar.models.url import RecipeURL


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    src = db.Column(db.String)
    dst = db.Column(db.String)
    domain = db.Column(db.String)
    image_src = db.Column(db.String)
    time = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    rating = db.Column(db.Float)
    ingredients = db.relationship(
        'RecipeIngredient',
        backref='recipe',
        passive_deletes='all'
    )
    directions = db.relationship(
        'RecipeDirection',
        backref='recipe',
        passive_deletes='all'
    )

    indexed_at = db.Column(db.DateTime)

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

    @property
    def recipe_url(self):
        return db.session.query(RecipeURL).get(self.dst)

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
            'dst': self.dst,
            'domain': self.domain,
            'url': self.url,
            'image_url': self.image_path,
            'nutrition': self.nutrition,
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

    @property
    def nutrition(self):
        all_ingredients_mass = sum([
            i.mass or 0
            for i in self.ingredients
        ])
        ingredients_with_nutrition_mass = sum([
            i.mass or 0
            for i in self.ingredients
            if i.nutrition
        ])

        # Only render nutritional content when it is known for 90%+ of the
        # recipe ingredients, by mass
        if ingredients_with_nutrition_mass < all_ingredients_mass * 0.9:
            return None

        totals = {
            c.name: 0
            for c in IngredientNutrition.__table__.columns
            if not c.primary_key and not c.foreign_keys
        }
        for ingredient in self.ingredients:
            if not ingredient.nutrition:
                continue
            for nutrient in totals.keys():
                totals[nutrient] += getattr(ingredient.nutrition, nutrient)
        for nutrient in totals.keys():
            totals[nutrient] = round(totals[nutrient], 2)
        return totals

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
        data['nutrition'] = self.nutrition
        return data
