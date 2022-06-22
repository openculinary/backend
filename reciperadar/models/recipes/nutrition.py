from reciperadar import db
from reciperadar.models.base import Storable


class Nutrition(Storable):
    __abstract__ = True

    carbohydrates = db.Column(db.Float)
    carbohydrates_units = db.Column(db.String)
    energy = db.Column(db.Float)
    energy_units = db.Column(db.String)
    fat = db.Column(db.Float)
    fat_units = db.Column(db.String)
    fibre = db.Column(db.Float)
    fibre_units = db.Column(db.String)
    protein = db.Column(db.Float)
    protein_units = db.Column(db.String)


class ProductNutrition(Nutrition):
    __tablename__ = 'product_nutrition'

    fk = db.ForeignKey(
        'products.id',
        deferrable=True,
        ondelete='cascade',
    )
    product_id = db.Column(db.String, fk, primary_key=True)


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
            carbohydrates_units=doc.get('carbohydrates_units'),
            energy=doc.get('energy'),
            energy_units=doc.get('energy_units'),
            fat=doc.get('fat'),
            fat_units=doc.get('fat_units'),
            fibre=doc.get('fibre'),
            fibre_units=doc.get('fibre_units'),
            protein=doc.get('protein'),
            protein_units=doc.get('protein_units'),
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
            carbohydrates_units=doc.get('carbohydrates_units'),
            energy=doc.get('energy'),
            energy_units=doc.get('energy_units'),
            fat=doc.get('fat'),
            fat_units=doc.get('fat_units'),
            fibre=doc.get('fibre'),
            fibre_units=doc.get('fibre_units'),
            protein=doc.get('protein'),
            protein_units=doc.get('protein_units'),
        )
