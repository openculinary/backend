from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import AbstractConcreteBase
import requests
from tldextract import TLDExtract

from reciperadar.models.base import Storable


class BaseURL(AbstractConcreteBase, Storable):
    __metaclass__ = ABC

    # By default TLDExtract pulls a subdomain suffix list from the web;
    # here we disable that behaviour - it falls back to a built-in snapshot
    tldextract = TLDExtract(suffix_list_urls=None)

    url = Column(String, primary_key=True)
    domain = Column(String)
    crawled_at = Column(DateTime)
    crawl_status = Column(Integer)

    class BackoffException(Exception):
        pass

    BACKOFFS = {
        404: timedelta(hours=1),
        429: timedelta(hours=1),
        500: timedelta(hours=1),
    }

    ERROR_MESSAGES = {
        404: 'Missing or incomplete recipe',
        429: 'Crawler rate-limit exceeded',
        500: 'Scraper failure occurred',
        501: 'Website not supported',
    }

    def __init__(self, url):
        url_info = self.tldextract(url)
        domain = f'{url_info.domain}.{url_info.suffix}'
        super().__init__(url=url, domain=domain)

    @abstractmethod
    def _make_request(self):
        pass

    @property
    def error_message(self):
        return self.ERROR_MESSAGES.get(self.crawl_status, 'Unknown error')

    def crawl(self):
        backoff = self.BACKOFFS.get(self.crawl_status)
        if backoff and (self.crawled_at + backoff) > datetime.utcnow():
            raise RecipeURL.BackoffException()

        response = self._make_request()
        self.crawl_status = response.status_code
        self.crawled_at = datetime.utcnow()
        return response


class CrawlURL(BaseURL):
    __tablename__ = 'crawl_urls'

    def _make_request(self):
        return requests.get(self.url)


class RecipeURL(BaseURL):
    __tablename__ = 'recipe_urls'

    def _make_request(self):
        return requests.post('http://crawler-service', data={'url': self.url})
