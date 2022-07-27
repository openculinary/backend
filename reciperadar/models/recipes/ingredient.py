from reciperadar import db
from reciperadar.models.base import Indexable, Storable
from reciperadar.models.recipes.nutrition import IngredientNutrition


class RecipeIngredient(Storable, Indexable):
    __tablename__ = "recipe_ingredients"

    recipe_fk = db.ForeignKey(column="recipes.id", ondelete="cascade")
    recipe_id = db.Column(db.String, recipe_fk, index=True)

    product_name_fk = db.ForeignKey(
        column="product_names.id",
        deferrable=True,
        ondelete="set null",
    )
    product_name_id = db.Column(db.String, product_name_fk, index=True)

    id = db.Column(db.String, primary_key=True)
    index = db.Column(db.Integer)
    description = db.Column(db.String)
    markup = db.Column(db.String)

    product_name = db.relationship("ProductName", uselist=False)
    nutrition = db.relationship(
        "IngredientNutrition", uselist=False, passive_deletes="all"
    )

    magnitude = db.Column(db.Float)
    magnitude_parser = db.Column(db.String)
    units = db.Column(db.String)
    units_parser = db.Column(db.String)
    product_is_plural = db.Column(db.Boolean)
    product_parser = db.Column(db.String)
    relative_density = db.Column(db.Float)
    verb = db.Column(db.String)

    @property
    def product(self):
        if self.product_name:
            return self.product_name.product

    @product.setter
    def product(self, value):
        if self.product_name:
            self.product_name.product = value

    @property
    def mass(self):
        if self.units == "g":
            return self.magnitude
        if self.units == "ml":
            return self.magnitude / self.relative_density

    @staticmethod
    def from_doc(doc):
        ingredient_id = doc.get("id") or RecipeIngredient.generate_id()
        nutrition = doc.get("nutrition")
        return RecipeIngredient(
            id=ingredient_id,
            index=doc["index"],
            description=doc["description"].strip(),
            markup=doc.get("markup"),
            product_name_id=doc["product"].get("product_id"),
            product_is_plural=doc["product"].get("is_plural"),
            product_parser=doc["product"].get("product_parser"),
            nutrition=IngredientNutrition.from_doc(nutrition) if nutrition else None,
            relative_density=doc.get("relative_density"),
            magnitude=doc.get("magnitude"),
            magnitude_parser=doc.get("magnitude_parser"),
            units=doc.get("units"),
            units_parser=doc.get("units_parser"),
            verb=doc.get("verb"),
        )

    def to_doc(self):
        data = super().to_doc()
        data["product"] = self.product.to_doc() if self.product else None
        data["product_name"] = (
            (
                self.product_name.plural
                if self.product_is_plural
                else self.product_name.singular
            )
            if self.product_name
            else None
        )
        data["nutrition"] = self.nutrition.to_doc() if self.nutrition else None
        return data
