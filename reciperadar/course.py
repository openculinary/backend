from reciperadar.base import Searchable


class Course(Searchable):

    def __init__(self):
        super().__init__(noun='courses')
