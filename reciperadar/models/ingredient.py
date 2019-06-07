from reciperadar.models.base import Searchable


class Ingredient(Searchable):

    @property
    def noun(self):
        return 'ingredients'
