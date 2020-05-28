from reciperadar import db
from reciperadar.models.base import Storable


class DirectionUtensil(Storable):
    __tablename__ = 'direction_utensils'

    fk = db.ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    utensil = db.Column(db.String)

    @staticmethod
    def from_doc(doc):
        utensil_id = doc.get('id') or DirectionUtensil.generate_id()
        return DirectionUtensil(
            id=utensil_id,
            utensil=doc['utensil'],
        )
