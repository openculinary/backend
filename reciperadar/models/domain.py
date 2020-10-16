from reciperadar import db
from reciperadar.models.base import Searchable, Storable


class Domain(Searchable, Storable):
    __tablename__ = 'domains'

    domain = db.Column(db.String, primary_key=True)
    image_src = db.Column(db.String)
