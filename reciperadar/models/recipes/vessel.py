from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)

from reciperadar.models.base import Storable


class DirectionVessel(Storable):
    __tablename__ = 'direction_vessels'

    fk = ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    vessel = Column(String)

    @staticmethod
    def from_doc(doc):
        vessel_id = doc.get('id') or DirectionVessel.generate_id()
        return DirectionVessel(
            id=vessel_id,
            vessel=doc['vessel'],
        )
