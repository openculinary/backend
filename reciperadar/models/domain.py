from reciperadar import db
from reciperadar.models.base import Storable


class Domain(Storable):
    __tablename__ = "domains"

    domain = db.Column(db.String, primary_key=True)
    image_enabled = db.Column(db.Boolean)
    image_src = db.Column(db.String)
    contact = db.Column(db.String)
