from reciperadar.models.base import Searchable, Storable


class Domain(Searchable, Storable):
    __tablename__ = 'domains'

    domain = Column(String, primary_key=True)
    image_src = Column(String)
