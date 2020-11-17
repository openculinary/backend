from pymmh3 import hash_bytes

from reciperadar import db
from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.direction import RecipeDirection
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.nutrition import (
    IngredientNutrition,
    RecipeNutrition,
)
from reciperadar.models.url import RecipeURL


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    src = db.Column(db.String)
    dst = db.Column(db.String)
    domain = db.Column(db.String)
    author = db.Column(db.String)
    author_url = db.Column(db.String)
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
    nutrition = db.relationship(
        'RecipeNutrition',
        backref='recipe',
        uselist=False,
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
            ingredient.product.product.singular: ingredient.product.product
            for ingredient in self.ingredients
        }
        return list(unique_products.values())

    @property
    def hidden(self):
        for ingredient in self.ingredients:
            if not ingredient.product.product.singular:
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
            dst=doc['dst'],
            domain=doc['domain'],
            author=doc.get('author'),
            author_url=doc.get('author_url'),
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
            nutrition=RecipeNutrition.from_doc(doc['nutrition'])
            if doc.get('nutrition') else None,
            servings=doc['servings'],
            time=doc['time'],
            rating=doc['rating']
        )

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
    def aggregate_ingredient_nutrition(self):
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
            totals[nutrient] = round(totals[nutrient] / self.servings, 2)
        return totals

    @property
    def is_dairy_free(self):
        return all([
            ingredient.product.product.is_dairy_free
            for ingredient in self.ingredients
        ])

    @property
    def is_gluten_free(self):
        return all([
            ingredient.product.product.is_gluten_free
            for ingredient in self.ingredients
        ])

    @property
    def is_vegan(self):
        return all([
            ingredient.product.product.is_vegan
            for ingredient in self.ingredients
        ])

    @property
    def is_vegetarian(self):
        return all([
            ingredient.product.product.is_vegetarian
            for ingredient in self.ingredients
        ])

    def to_doc(self):
        data = super().to_doc()
        data['directions'] = [
            direction.to_doc()
            for direction in self.directions
        ]
        data['ingredients'] = [
            ingredient.to_doc()
            for ingredient in self.ingredients
            if ingredient.product
        ]
        data['contents'] = self.contents
        data['product_count'] = len(self.products)
        data['hidden'] = self.hidden
        data['nutrition'] = self.nutrition.to_doc() \
            if self.nutrition else self.aggregate_ingredient_nutrition
        data['is_dairy_free'] = self.is_dairy_free
        data['is_gluten_free'] = self.is_gluten_free
        data['is_vegan'] = self.is_vegan
        data['is_vegetarian'] = self.is_vegetarian
        return data
