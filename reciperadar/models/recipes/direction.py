from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from reciperadar.models.base import Storable
from reciperadar.models.recipes.appliance import DirectionAppliance
from reciperadar.models.recipes.utensil import DirectionUtensil


class RecipeDirection(Storable):
    __tablename__ = 'recipe_directions'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    index = Column(Integer)
    description = Column(String)
    appliances = relationship(
        'DirectionAppliance',
        backref='recipe_directions',
        passive_deletes='all'
    )
    utensils = relationship(
        'DirectionUtensil',
        backref='recipe_directions',
        passive_deletes='all'
    )

    @staticmethod
    def from_doc(doc, matches=None):
        direction_id = doc.get('id') or RecipeDirection.generate_id()
        return RecipeDirection(
            id=direction_id,
            index=doc.get('index'),  # TODO
            description=doc['description'],
            appliances=[
                DirectionAppliance.from_doc(appliance)
                for appliance in doc.get('appliances', [])
            ],
            utensils=[
                DirectionUtensil.from_doc(utensil)
                for utensil in doc.get('utensils', [])
            ]
        )

    def to_doc(self):
        data = super().to_doc()
        data['appliances'] = [
            appliance.to_doc()
            for appliance in self.appliances
        ]
        data['utensils'] = [
            utensil.to_doc()
            for utensil in self.appliances
        ]
        return data

    def to_dict(self):
        return {'tokens': [{
            'type': 'text',
            'value': self.description
        }]}
