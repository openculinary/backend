from sqlalchemy import Column, DateTime, Integer, String

from reciperadar.models.base import Storable


class RecipeURL(Storable):
    __tablename__ = 'recipe_urls'

    url = Column(String, primary_key=True)
    crawled_at = Column(DateTime)
    crawl_status = Column(Integer)
