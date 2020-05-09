from reciperadar.models.base import Storable


class Domain(Storable):
    __tablename__ = 'domains'

    domain = Column(String, primary_key=True)
    image_src = Column(String)
