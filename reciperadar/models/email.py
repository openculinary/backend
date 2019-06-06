from datetime import datetime
from sqlalchemy import Column, DateTime, String

from reciperadar.models.base import Storable


class Email(Storable):
    __tablename__ = 'emails'

    email = Column(String, primary_key=True)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime)
