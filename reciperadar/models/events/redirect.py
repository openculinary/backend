from sqlalchemy import (
    Column,
    String,
)
from reciperadar.models.events.base import BaseEvent


class RedirectEvent(BaseEvent):
    __tablename__ = 'redirects'

    recipe_id = Column(String)
    domain = Column(String)
    src = Column(String)
