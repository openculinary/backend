from sqlalchemy.dialects import postgresql

from reciperadar import db
from reciperadar.models.events.base import BaseEvent


class SearchEvent(BaseEvent):
    __tablename__ = "searches"

    path = db.Column(db.String)
    include = db.Column(postgresql.ARRAY(db.String))
    exclude = db.Column(postgresql.ARRAY(db.String))
    equipment = db.Column(postgresql.ARRAY(db.String))
    dietary_properties = db.Column(postgresql.ARRAY(db.String))
    offset = db.Column(db.Integer)
    limit = db.Column(db.Integer)
    sort = db.Column(db.String)
    results_ids = db.Column(postgresql.ARRAY(db.String))
    results_total = db.Column(db.Integer)
