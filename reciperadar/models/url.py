from sqlalchemy import Column, DateTime, Integer, String
import tldextract

from reciperadar.models.base import Storable


class RecipeURL(Storable):
    __tablename__ = 'recipe_urls'

    def __init__(self, *args, **kwargs):
        if 'url' in kwargs:
            url_info = tldextract.extract(kwargs['url'])
            domain = f'{url_info.domain}.{url_info.suffix}'
            kwargs['domain'] = domain
        super().__init__(*args, **kwargs)

    url = Column(String, primary_key=True)
    domain = Column(String)
    crawled_at = Column(DateTime)
    crawl_status = Column(Integer)
