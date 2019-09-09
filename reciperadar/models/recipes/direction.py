from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)

from reciperadar.models.base import Storable


class RecipeDirection(Storable):
    __tablename__ = 'recipe_directions'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    description = Column(String)

    @staticmethod
    def from_doc(doc, matches=None):
        description = doc['description'].strip()

        direction_id = doc.get('id') or RecipeDirection.generate_id()
        return RecipeDirection(
            id=direction_id,
            description=description
        )

    def to_dict(self):
        return {'tokens': [{
            'type': 'text',
            'value': self.description
        }]}
