from reciperadar import db
from reciperadar.models.events.base import BaseEvent


class RedirectEvent(BaseEvent):
    __tablename__ = "redirects"

    recipe_id = db.Column(db.String)
    domain = db.Column(db.String)
    src = db.Column(db.String)
