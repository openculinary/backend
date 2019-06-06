from reciperadar.models.base import Searchable


class Ingredient(Searchable):

    def __init__(self):
        super().__init__(noun='ingredients')
