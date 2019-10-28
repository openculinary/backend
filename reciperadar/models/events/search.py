from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.dialects import postgresql

from reciperadar.models.events.base import BaseEvent


class SearchEvent(BaseEvent):
    __tablename__ = 'searches'

    include = Column(postgresql.ARRAY(String))
    exclude = Column(postgresql.ARRAY(String))
    equipment = Column(postgresql.ARRAY(String))
    offset = Column(Integer)
    limit = Column(Integer)
    sort = Column(String)
    results_ids = Column(postgresql.ARRAY(String))
    results_total = Column(Integer)
