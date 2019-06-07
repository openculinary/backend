from reciperadar.models.base import Searchable


class Course(Searchable):

    @property
    def noun(self):
        return 'courses'
