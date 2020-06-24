from reciperadar import db
from reciperadar.models.base import Storable


class DirectionAppliance(Storable):
    __tablename__ = 'direction_appliances'

    fk = db.ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    appliance = db.Column(db.String)

    @staticmethod
    def from_doc(doc):
        appliance_id = doc.get('id') or DirectionAppliance.generate_id()
        return DirectionAppliance(
            id=appliance_id,
            appliance=doc['appliance'],
        )
