from reciperadar import db
from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.product import IngredientProduct
from reciperadar.models.recipes.nutrition import IngredientNutrition


class RecipeIngredient(Storable, Searchable):
    __tablename__ = 'recipe_ingredients'

    fk = db.ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    index = db.Column(db.Integer)
    description = db.Column(db.String)
    markup = db.Column(db.String)
    product = db.relationship(
        'IngredientProduct',
        backref='recipe_ingredient',
        uselist=False,
        passive_deletes='all'
    )
    nutrition = db.relationship(
        'IngredientNutrition',
        backref='recipe_ingredient',
        uselist=False,
        passive_deletes='all'
    )

    magnitude = db.Column(db.Float)
    magnitude_parser = db.Column(db.String)
    units = db.Column(db.String)
    units_parser = db.Column(db.String)
    verb = db.Column(db.String)

    @staticmethod
    def from_doc(doc):
        ingredient_id = doc.get('id') or RecipeIngredient.generate_id()
        return RecipeIngredient(
            id=ingredient_id,
            index=doc.get('index'),  # TODO
            description=doc['description'].strip(),
            markup=doc.get('markup'),
            product=IngredientProduct.from_doc(doc['product']),
            nutrition=IngredientNutrition.from_doc(doc['nutrition'])
            if 'nutrition' in doc else None,
            magnitude=doc.get('magnitude') or doc.get('quantity'),  # TODO
            magnitude_parser=(
                doc.get('magnitude_parser') or doc.get('quantity_parser')
            ),  # TODO
            units=doc.get('units'),
            units_parser=doc.get('units_parser'),
            verb=doc.get('verb')
        )

    def to_dict(self, include=None):
        return {
            'markup': self.markup,
            'product': self.product.to_dict(include),
            'quantity': {
                'magnitude': self.magnitude,
                'units': self.units,
            }
        }

    def to_doc(self):
        data = super().to_doc()
        data['product'] = self.product.to_doc()
        return data
