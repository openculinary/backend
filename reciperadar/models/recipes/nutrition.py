from reciperadar import db
from reciperadar.models.base import Storable


class IngredientNutrition(Storable):
    __tablename__ = 'ingredient_nutrition'

    fk = db.ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    carbohydrates = db.Column(db.Float)
    energy = db.Column(db.Float)
    fat = db.Column(db.Float)
    fibre = db.Column(db.Float)
    protein = db.Column(db.Float)

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
