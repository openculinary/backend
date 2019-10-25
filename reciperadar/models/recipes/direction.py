from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)

from reciperadar.models.base import Storable


class RecipeDirection(Storable):
    __tablename__ = 'recipe_directions'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    index = Column(Integer)
    description = Column(String)

    @staticmethod
    def from_doc(doc, matches=None):
        direction_id = doc.get('id') or RecipeDirection.generate_id()
        return RecipeDirection(
            id=direction_id,
            index=doc.get('index'),  # TODO
            description=doc['description'].strip()
        )

    def to_dict(self):
        return {'tokens': [{
            'type': 'text',
            'value': self.description
        }]}
