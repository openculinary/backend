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
from reciperadar.models.recipes.vessel import DirectionVessel


class RecipeDirection(Storable):
    __tablename__ = 'recipe_directions'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    index = Column(Integer)
    description = Column(String)
    markup = Column(String)
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
    vessels = relationship(
        'DirectionVessel',
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
            markup=doc.get('markup'),
            appliances=[
                DirectionAppliance.from_doc(appliance)
                for appliance in doc.get('appliances', [])
            ],
            utensils=[
                DirectionUtensil.from_doc(utensil)
                for utensil in doc.get('utensils', [])
            ],
            vessels=[
                DirectionVessel.from_doc(vessel)
                for vessel in doc.get('vessels', [])
            ]
        )

    def to_doc(self):
        data = super().to_doc()
        data['equipment'] = [
            {'equipment': appliance.appliance}
            for appliance in self.appliances
        ] + [
            {'equipment': utensil.utensil}
            for utensil in self.utensils
        ] + [
            {'equipment': vessel.vessel}
            for vessel in self.vessels
        ]
        return data

    def to_dict(self):
        return {
            'markup': self.markup,
            'tokens': [{
                'type': 'text',
                'value': self.description,
            }],
        }
