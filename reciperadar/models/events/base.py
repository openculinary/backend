from abc import ABC
from datetime import datetime
from uuid import uuid4

from reciperadar import db
from reciperadar.models.base import Storable


class BaseEvent(Storable):
    __abstract__ = True
    __metaclass__ = ABC

    event_id = db.Column(db.String, default=uuid4, primary_key=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    suspected_bot = db.Column(db.Boolean, default=False)
