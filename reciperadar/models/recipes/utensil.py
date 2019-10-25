from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)

from reciperadar.models.base import Storable


class DirectionUtensil(Storable):
    __tablename__ = 'direction_utensils'

    fk = ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    utensil = Column(String)

    @staticmethod
    def from_doc(doc):
        utensil_id = doc.get('id') or DirectionUtensil.generate_id()
        return DirectionUtensil(
            id=utensil_id,
            utensil=doc['utensil'],
        )
