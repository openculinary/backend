from reciperadar import db
from reciperadar.models.base import Storable


class DirectionVessel(Storable):
    __tablename__ = 'direction_vessels'

    fk = db.ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    vessel = db.Column(db.String)

    @staticmethod
    def from_doc(doc):
        vessel_id = doc.get('id') or DirectionVessel.generate_id()
        return DirectionVessel(
            id=vessel_id,
            vessel=doc['vessel'],
        )
