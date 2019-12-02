from abc import ABC
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
)
from uuid import uuid4
from sqlalchemy.ext.declarative import AbstractConcreteBase

from reciperadar.models.base import Storable


class BaseEvent(AbstractConcreteBase, Storable):
    __metaclass__ = ABC

    event_id = Column(String, default=uuid4, primary_key=True)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    suspected_bot = Column(Boolean, default=False)
