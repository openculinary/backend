from reciperadar import db
from reciperadar.models.base import Storable


class DirectionEquipment(Storable):
    __tablename__ = 'direction_equipment'

    fk = db.ForeignKey('recipe_directions.id', ondelete='cascade')
    direction_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    category = db.Column(db.String)

    @staticmethod
    def from_doc(doc):
        equipment_id = doc.get('id') or DirectionEquipment.generate_id()
        return DirectionEquipment(
            id=equipment_id,
            name=doc['name'],
            category=doc['category'],
        )

    def to_doc(self):
        data = super().to_doc()
        # TODO: Remove backwards-compatible search index field
        data['equipment'] = self.name
        return data
