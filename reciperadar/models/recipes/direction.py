from xml.etree import ElementTree

from reciperadar import db
from reciperadar.models.base import Storable
from reciperadar.models.recipes.appliance import DirectionAppliance
from reciperadar.models.recipes.utensil import DirectionUtensil
from reciperadar.models.recipes.vessel import DirectionVessel


class RecipeDirection(Storable):
    __tablename__ = 'recipe_directions'

    fk = db.ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    index = db.Column(db.Integer)
    description = db.Column(db.String)
    markup = db.Column(db.String)
    appliances = db.relationship(
        'DirectionAppliance',
        backref='recipe_directions',
        passive_deletes='all'
    )
    utensils = db.relationship(
        'DirectionUtensil',
        backref='recipe_directions',
        passive_deletes='all'
    )
    vessels = db.relationship(
        'DirectionVessel',
        backref='recipe_directions',
        passive_deletes='all'
    )

    @staticmethod
    def _build_item(item, category, category_class):
        item_classes = set(item.attrib.get('class', '').split())
        if 'equipment' not in item_classes:
            return
        if category not in item_classes:
            return
        doc = {category: item.text}
        return category_class.from_doc(doc)

    @staticmethod
    def _parse_equipment(markup):
        equipment = {
            'appliances': [],
            'utensils': [],
            'vessels': [],
        }
        if not markup:
            return equipment

        category_classes = {
            'appliances': DirectionAppliance,
            'utensils': DirectionUtensil,
            'vessels': DirectionVessel,
        }

        doc = ElementTree.fromstring(f'<xml>{markup}</xml>')
        for item in doc.findall('mark'):
            for category in equipment:
                cls = category_classes[category]
                obj = RecipeDirection._build_item(item, category[:-1], cls)
                equipment[category].append(obj) if obj else None
        return equipment

    @staticmethod
    def from_doc(doc, matches=None):
        direction_id = doc.get('id') or RecipeDirection.generate_id()
        equipment = RecipeDirection._parse_equipment(doc['markup'])
        return RecipeDirection(
            id=direction_id,
            index=doc.get('index'),  # TODO
            description=doc['description'],
            markup=doc['markup'],
            **equipment
        )

    def to_doc(self):
        data = super().to_doc()
        data['equipment'] = [
            {'equipment': appliance.appliance}
            for appliance in self.appliances
        ] + [
            {'equipment': utensil.utensil}
            for utensil in self.utensils
        ] + [
            {'equipment': vessel.vessel}
            for vessel in self.vessels
        ]
        return data

    def to_dict(self):
        return {
            'markup': self.markup,
        }
