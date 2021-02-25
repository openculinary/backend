from xml.etree import ElementTree

from reciperadar import db
from reciperadar.models.base import Storable
from reciperadar.models.recipes.equipment import DirectionEquipment


class RecipeDirection(Storable):
    __tablename__ = 'recipe_directions'

    fk = db.ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    index = db.Column(db.Integer)
    description = db.Column(db.String)
    markup = db.Column(db.String)
    equipment = db.relationship(
        'DirectionEquipment',
        passive_deletes='all'
    )

    @staticmethod
    def from_doc(doc, matches=None):
        direction_id = doc.get('id') or RecipeDirection.generate_id()
        equipment = RecipeDirection._parse_equipment(doc['markup'])
        return RecipeDirection(
            id=direction_id,
            index=doc['index'],
            description=doc['description'],
            markup=doc['markup'],
            equipment=[
                DirectionEquipment.from_doc(entity)
                for entity in doc['entities']
                if entity.get('type') == 'equipment'
            ],
        )

    def to_doc(self):
        data = super().to_doc()
        data['equipment'] = [
            equipment.to_doc() for equipment in self.equipment
        ]
        return data
