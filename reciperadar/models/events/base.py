from abc import ABC
from datetime import UTC, datetime
from uuid import uuid4

from reciperadar import db
from reciperadar.models.base import Storable


class BaseEvent(Storable):
    __abstract__ = True
    __metaclass__ = ABC
    __table_args__ = {"schema": "events"}

    event_id = db.Column(db.String, default=uuid4, primary_key=True)
    logged_at = db.Column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(tz=UTC),
        nullable=False,
    )
    suspected_bot = db.Column(db.Boolean, default=False)
