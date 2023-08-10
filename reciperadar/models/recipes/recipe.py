from pymmh3 import hash_bytes

from reciperadar import db
from reciperadar.models.base import Indexable, Storable
from reciperadar.models.recipes.direction import RecipeDirection
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.nutrition import (
    IngredientNutrition,
    RecipeNutrition,
)
from reciperadar.models.url import RecipeURL


class Recipe(Storable, Indexable):
    __tablename__ = "recipes"

    redirected_fk = db.ForeignKey(
        "recipes.id",
        deferrable=True,
        ondelete="cascade",
        onupdate="cascade",
    )

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    src = db.Column(db.String)
    dst = db.Column(db.String)
    domain = db.Column(db.String)
    author = db.Column(db.String)
    author_url = db.Column(db.String)
    image_enabled = db.Column(db.Boolean)
    image_src = db.Column(db.String)
    time = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    rating = db.Column(db.Float)
    ingredients = db.relationship("RecipeIngredient", passive_deletes="all")
    directions = db.relationship("RecipeDirection", passive_deletes="all")
    nutrition = db.relationship("RecipeNutrition", uselist=False, passive_deletes="all")

    indexed_at = db.Column(db.DateTime)

    redirected_id = db.Column(db.String, redirected_fk)
    redirected_at = db.Column(db.DateTime)

    @property
    def noun(self):
        return "recipes"

    @property
    def url(self):
        return f"/#action=view&id={self.id}"

    @property
    def product_names(self):
        unique_products = {
            ingredient.product_name.singular: ingredient.product_name
            for ingredient in self.ingredients
            if ingredient.product_name
        }
        return list(unique_products.values())

    @property
    def hidden(self):
        return not all([ingredient.product for ingredient in self.ingredients])

    @property
    def recipe_url(self):
        return db.session.get(RecipeURL, self.dst)

    @staticmethod
    def from_doc(doc):
        src_hash = hash_bytes(doc["src"]).encode("utf-8")
        recipe_id = doc.get("id") or Recipe.generate_id(src_hash)
        return Recipe(
            id=recipe_id,
            title=doc["title"],
            src=doc["src"],
            dst=doc["dst"],
            domain=doc["domain"],
            author=doc.get("author"),
            author_url=doc.get("author_url"),
            image_src=doc.get("image_src"),
            ingredients=[
                RecipeIngredient.from_doc(ingredient)
                for ingredient in doc["ingredients"]
                if ingredient["description"].strip()
            ],
            directions=[
                RecipeDirection.from_doc(direction)
                for direction in doc.get("directions") or []
                if direction["description"].strip()
            ],
            nutrition=RecipeNutrition.from_doc(doc["nutrition"])
            if doc.get("nutrition")
            else None,
            servings=doc["servings"],
            time=doc["time"],
            rating=doc["rating"],
        )

    @property
    def image_path(self):
        return f"images/recipes/{self.id}.png"

    @property
    def contents(self):
        contents = set()
        for product_name in self.product_names:
            contents |= set(product_name.contents or [])
        return list(contents)

    @property
    def aggregate_ingredient_nutrition(self):
        all_ingredients_mass = sum([i.mass or 0 for i in self.ingredients])
        ingredients_with_nutrition_mass = sum(
            [i.mass or 0 for i in self.ingredients if i.nutrition]
        )

        # Only render nutritional content when it is known for 90%+ of the
        # recipe ingredients, by mass
        if ingredients_with_nutrition_mass < all_ingredients_mass * 0.9:
            return None

        units = {}
        totals = {
            c.name: 0
            for c in IngredientNutrition.__table__.columns
            if f"{c.name}_units" in IngredientNutrition.__table__.columns
        }
        for ingredient in self.ingredients:
            if not ingredient.nutrition:
                continue
            for nutrient in totals.keys():
                magnitude = getattr(ingredient.nutrition, nutrient) or 0
                unit = getattr(ingredient.nutrition, f"{nutrient}_units")
                # TODO: Handle mixed nutritional units within recipes (pint?)
                if nutrient in units and units[nutrient] != unit:
                    return None
                totals[nutrient] += magnitude
                units[nutrient] = unit
        for nutrient in totals.keys():
            totals[nutrient] = round(totals[nutrient] / self.servings, 2)
        return {
            **{f"{nutrient}": total for nutrient, total in totals.items()},
            **{f"{nutrient}_units": unit for nutrient, unit in units.items()},
        }

    @property
    def is_dairy_free(self):
        return all(
            [
                ingredient.product.is_dairy_free
                for ingredient in self.ingredients
                if ingredient.product
            ]
        )

    @property
    def is_gluten_free(self):
        return all(
            [
                ingredient.product.is_gluten_free
                for ingredient in self.ingredients
                if ingredient.product
            ]
        )

    @property
    def is_vegan(self):
        return all(
            [
                ingredient.product.is_vegan
                for ingredient in self.ingredients
                if ingredient.product
            ]
        )

    @property
    def is_vegetarian(self):
        return all(
            [
                ingredient.product.is_vegetarian
                for ingredient in self.ingredients
                if ingredient.product
            ]
        )

    def to_doc(self):
        data = super().to_doc()
        data["directions"] = [direction.to_doc() for direction in self.directions]
        data["ingredients"] = [ingredient.to_doc() for ingredient in self.ingredients]
        data["contents"] = self.contents
        data["product_count"] = len(self.product_names)
        data["hidden"] = self.hidden
        data["nutrition"] = (
            self.nutrition.to_doc()
            if self.nutrition
            else self.aggregate_ingredient_nutrition
        )
        data["nutrition_source"] = "crawler" if self.nutrition else "aggregation"
        data["is_dairy_free"] = self.is_dairy_free
        data["is_gluten_free"] = self.is_gluten_free
        data["is_vegan"] = self.is_vegan
        data["is_vegetarian"] = self.is_vegetarian
        return data
