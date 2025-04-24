from reciperadar import db
from reciperadar.models.base import Indexable, Storable
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.nutrition import RecipeNutrition
from reciperadar.models.url import BaseURL, RecipeURL


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
    time = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    rating = db.Column(db.Float)
    ingredients = db.relationship("RecipeIngredient", passive_deletes="all")
    nutrition = db.relationship("RecipeNutrition", uselist=False, passive_deletes="all")

    indexed_at = db.Column(db.TIMESTAMP(timezone=True))

    not_found = db.Column(db.Boolean, default=False)
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
        return unique_products.values()

    @property
    def hidden(self):
        if self.not_found:
            return True
        if self.redirected_id:
            return True
        if not all(ingredient.product for ingredient in self.ingredients):
            return True
        return False

    @property
    def recipe_url(self):
        return db.session.get(RecipeURL, self.id)

    @staticmethod
    def from_doc(doc):
        recipe_id = doc.get("id") or BaseURL.url_to_id(doc["src"])
        return Recipe(
            id=recipe_id,
            title=doc["title"],
            src=doc["src"],
            dst=doc["dst"],
            domain=doc["domain"],
            author=doc.get("author"),
            author_url=doc.get("author_url"),
            ingredients=[
                RecipeIngredient.from_doc(ingredient)
                for ingredient in doc["ingredients"]
                if ingredient["description"].strip()
            ],
            nutrition=(
                RecipeNutrition.from_doc(doc["nutrition"])
                if doc.get("nutrition")
                else None
            ),
            servings=doc["servings"],
            time=doc["time"],
            rating=doc["rating"],
            indexed_at=doc.get("indexed_at"),
            not_found=doc.get("not_found"),
            redirected_id=doc.get("redirected_id"),
            redirected_at=doc.get("redirected_at"),
        )

    @property
    def image_path(self):
        return f"images/recipes/{self.id}.png"

    @property
    def contents(self):
        contents = set()
        for product_name in self.product_names:
            contents |= set(product_name.contents or [])
        return sorted(contents)

    @property
    def is_dairy_free(self):
        return all(
            ingredient.product.is_dairy_free
            for ingredient in self.ingredients
            if ingredient.product
        )

    @property
    def is_gluten_free(self):
        return all(
            ingredient.product.is_gluten_free
            for ingredient in self.ingredients
            if ingredient.product
        )

    @property
    def is_vegan(self):
        return all(
            ingredient.product.is_vegan
            for ingredient in self.ingredients
            if ingredient.product
        )

    @property
    def is_vegetarian(self):
        return all(
            ingredient.product.is_vegetarian
            for ingredient in self.ingredients
            if ingredient.product
        )

    def to_doc(self):
        data = super().to_doc()
        data["ingredients"] = [ingredient.to_doc() for ingredient in self.ingredients]
        data["contents"] = self.contents
        data["product_count"] = len(self.product_names)
        data["hidden"] = self.hidden
        data["nutrition"] = self.nutrition.to_doc() if self.nutrition else None
        data["nutrition_source"] = "crawler" if self.nutrition else None
        if "not_found" in data and not data["not_found"]:
            del data["not_found"]
        data["redirected_id"] = self.redirected_id  # explicit foreign key serialization
        data["is_dairy_free"] = self.is_dairy_free
        data["is_gluten_free"] = self.is_gluten_free
        data["is_vegan"] = self.is_vegan
        data["is_vegetarian"] = self.is_vegetarian
        return data
