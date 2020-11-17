from reciperadar import db
from reciperadar.models.base import Storable


class Nutrition(Storable):
    __abstract__ = True

    carbohydrates = db.Column(db.Float)
    energy = db.Column(db.Float)
    fat = db.Column(db.Float)
    fibre = db.Column(db.Float)
    protein = db.Column(db.Float)


class ProductNutrition(Nutrition):
    __tablename__ = 'product_nutrition'

    fk = db.ForeignKey('products.id', deferrable=True)
    product_id = db.Column(db.String, fk, primary_key=True)

    @staticmethod
    def from_doc(doc):
        return ProductNutrition(
            carbohydrates=doc.get('carbohydrates'),
            energy=doc.get('energy'),
            fat=doc.get('fat'),
            fibre=doc.get('fibre'),
            protein=doc.get('protein'),
        )


class IngredientNutrition(Nutrition):
    __tablename__ = 'ingredient_nutrition'

    fk = db.ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)

    @staticmethod
    def from_doc(doc):
        nutrition_id = doc.get('id') or IngredientNutrition.generate_id()
        return IngredientNutrition(
            id=nutrition_id,
            carbohydrates=doc.get('carbohydrates'),
            energy=doc.get('energy'),
            fat=doc.get('fat'),
            fibre=doc.get('fibre'),
            protein=doc.get('protein'),
        )


class RecipeNutrition(Nutrition):
    __tablename__ = 'recipe_nutrition'

    fk = db.ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)

    @staticmethod
    def from_doc(doc):
        nutrition_id = doc.get('id') or RecipeNutrition.generate_id()
        return RecipeNutrition(
            id=nutrition_id,
            carbohydrates=doc.get('carbohydrates'),
            energy=doc.get('energy'),
            fat=doc.get('fat'),
            fibre=doc.get('fibre'),
            protein=doc.get('protein'),
        )
