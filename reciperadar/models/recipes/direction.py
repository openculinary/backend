from functools import cached_property

from reciperadar import db
from reciperadar.models.base import Storable
from reciperadar.models.recipes.equipment import DirectionEquipment


class RecipeDirection(Storable):
    __tablename__ = "recipe_directions"

    fk = db.ForeignKey("recipes.id", ondelete="cascade")
    recipe_id = db.Column(db.String, fk, index=True)

    id = db.Column(db.String, primary_key=True)
    index = db.Column(db.Integer)
    description = db.Column(db.String)
    markup = db.Column(db.String)
    equipment = db.relationship("DirectionEquipment", passive_deletes="all")

    @staticmethod
    def _filter_markup(markup):
        if not markup:
            return
        include = 0
        for char in markup:
            if char == "<" and include == 0:
                include = 2
            elif char == ">":
                include -= 1
                if include == 0:
                    yield char
            if include > 0:
                yield char

    @cached_property
    def equipment_names(self):
        equipment_names = set()
        for item in self.equipment:
            equipment_names.add(item.name)
        return list(equipment_names)

    @staticmethod
    def from_doc(doc, matches=None):
        direction_id = doc.get("id") or RecipeDirection.generate_id()
        return RecipeDirection(
            id=direction_id,
            index=doc["index"],
            description=None,  # doc["description"],
            markup=str().join(RecipeDirection._filter_markup(doc["markup"])),
            equipment=[
                DirectionEquipment.from_doc(entity)
                for entity in doc["entities"]
                if entity.get("type") == "equipment"
            ],
        )

    def to_doc(self):
        data = super().to_doc()
        data["equipment"] = [equipment.to_doc() for equipment in self.equipment]
        return data
