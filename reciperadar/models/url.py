from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import requests
from tld import get_tld

from reciperadar import db
from reciperadar.models.base import Storable


class BaseURL(Storable):
    __abstract__ = True
    __metaclass__ = ABC

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
        598: 'Network read timeout error',
    }

    def __init__(self, *args, **kwargs):
        if 'url' in kwargs:
            url_info = get_tld(
                kwargs['url'],
                as_object=True,
                search_private=False
            )
            kwargs['domain'] = url_info.fld
        super().__init__(*args, **kwargs)

    url = db.Column(db.String, primary_key=True)
    domain = db.Column(db.String)
    crawled_at = db.Column(db.DateTime)
    crawl_status = db.Column(db.Integer)
    crawler_version = db.Column(db.String)

    @abstractmethod
    def _make_request(self):
        pass

    @property
    def error_message(self):
        return self.ERROR_MESSAGES.get(self.crawl_status, 'Unknown error')

    def crawl(self):
        backoff = self.BACKOFFS.get(self.crawl_status)
        now = datetime.utcnow()
        if self.crawled_at and backoff and self.crawled_at + backoff > now:
            raise RecipeURL.BackoffException()

        try:
            response = self._make_request()
        except requests.exceptions.Timeout:
            response = requests.Response()
            response.status_code = 598

        if response.ok:
            metadata = response.json().get('metadata', {})
            self.crawler_version = metadata.get('service_version')

        self.crawl_status = response.status_code
        self.crawled_at = now
        return response


class CrawlURL(BaseURL):
    __tablename__ = 'crawl_urls'

    resolves_to = db.Column(db.String, index=True)

    def _make_request(self):
        response = requests.post(
            url='http://crawler-service/resolve',
            data={'url': self.url}
        )
        if response.ok:
            self.resolves_to = response.json()['url']['resolves_to']
        return response


class RecipeURL(BaseURL):
    __tablename__ = 'recipe_urls'

    recipe_scrapers_version = db.Column(db.String, index=True)

    def find_earliest_crawl(self):
        earliest_crawl = (
            db.session.query(CrawlURL)
            .filter_by(resolves_to=self.url)
            .cte(recursive=True)
        )

        previous_step = db.aliased(earliest_crawl)
        earliest_crawl = earliest_crawl.union(
            db.session.query(CrawlURL)
            .filter_by(resolves_to=previous_step.c.url)
        )

        return (
            db.session.query(earliest_crawl)
            .order_by(earliest_crawl.c.crawled_at.asc())
            .first()
        )

    def find_latest_crawl(self):
        latest_crawl = (
            db.session.query(CrawlURL)
            .filter_by(resolves_to=self.url)
            .cte(recursive=True)
        )

        previous_step = db.aliased(latest_crawl)
        latest_crawl = latest_crawl.union(
            db.session.query(CrawlURL)
            .filter_by(url=previous_step.c.resolves_to)
        )

        return (
            db.session.query(latest_crawl)
            .order_by(latest_crawl.c.crawled_at.desc())
            .first()
        )

    def _make_request(self):
        response = requests.post(
            url='http://crawler-service/crawl',
            data={'url': self.url}
        )
        if response.ok:
            metadata = response.json().get('metadata', {})
            self.recipe_scrapers_version = metadata['recipe_scrapers_version']
        return response
