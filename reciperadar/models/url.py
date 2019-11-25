from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Integer, String
import requests
from tldextract import TLDExtract

from reciperadar.models.base import Storable


class CrawlURL(Storable):

    # By default TLDExtract pulls a subdomain suffix list from the web;
    # here we disable that behaviour - it falls back to a built-in snapshot
    tldextract = TLDExtract(suffix_list_urls=None)

    src = Column(String, primary_key=True)
    src_domain = Column(String)
    dst = Column(String)

    def __init__(self, src):
        src_info = self.tldextract(src)
        src_domain = f'{src_info.domain}.{src_info.suffix}'
        super().__init__(src=src, src_domain=src_domain)

    def resolve(self):
        response = requests.get(self.src)
        if response.ok:
            self.dst = response.url


class RecipeURL(Storable):
    __tablename__ = 'recipe_urls'

    BACKOFFS = {
        404: timedelta(hours=1),
        429: timedelta(hours=1),
        500: timedelta(hours=1),
    }

    class BackoffException(Exception):
        pass

    ERROR_MESSAGES = {
        404: 'Missing or incomplete recipe',
        429: 'Crawler rate-limit exceeded',
        500: 'Scraper failure occurred',
        501: 'Website not supported',
    }

    # By default TLDExtract pulls a subdomain suffix list from the web;
    # here we disable that behaviour - it falls back to a built-in snapshot
    tldextract = TLDExtract(suffix_list_urls=None)

    def __init__(self, *args, **kwargs):
        if 'url' in kwargs:
            url_info = self.tldextract(kwargs['url'])
            domain = f'{url_info.domain}.{url_info.suffix}'
            kwargs['domain'] = domain
        super().__init__(*args, **kwargs)

    url = Column(String, primary_key=True)
    domain = Column(String)
    crawled_at = Column(DateTime)
    crawl_status = Column(Integer)

    @property
    def error_message(self):
        return self.ERROR_MESSAGES.get(self.crawl_status, 'Unknown error')

    def crawl(self):
        backoff = self.BACKOFFS.get(self.crawl_status)
        if backoff and (self.crawled_at + backoff) > datetime.utcnow():
            raise RecipeURL.BackoffException()

        data = {'url': self.url}
        response = requests.post('http://crawler-service', data=data)

        self.crawl_status = response.status_code
        self.crawled_at = datetime.utcnow()
        response.raise_for_status()

        return response.json()
