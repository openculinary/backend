from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)

from reciperadar.models.base import Storable


class DirectionAppliance(Storable):
    __tablename__ = 'direction_appliances'

    fk = ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    appliance = Column(String)

    @staticmethod
    def from_doc(doc):
        appliance_id = doc.get('id') or DirectionAppliance.generate_id()
        return DirectionAppliance(
            id=appliance_id,
            appliance=doc['appliance'],
        )
