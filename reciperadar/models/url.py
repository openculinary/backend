from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import httpx
from pymmh3 import hash_bytes

from reciperadar import db
from reciperadar.models.base import Storable


class BaseURL(Storable):
    __abstract__ = True
    __metaclass__ = ABC

    BACKOFFS = {
        404: timedelta(days=10),
        429: timedelta(hours=1),
        500: timedelta(hours=1),
    }

    class BackoffException(Exception):
        pass

    ERROR_MESSAGES = {
        404: "Missing or incomplete recipe",
        429: "Crawler rate-limit exceeded",
        500: "Scraper failure occurred",
        501: "Website not supported",
        598: "Network read timeout error",
    }

    @staticmethod
    def url_to_id(url: str) -> str:
        url_hash = hash_bytes(url).encode("utf-8")
        return BaseURL.generate_id(url_hash)

    def __init__(self, *args, **kwargs):
        if "url" in kwargs:
            kwargs["id"] = BaseURL.url_to_id(kwargs["url"])
            kwargs["domain"] = urlparse(kwargs["url"]).netloc
            del kwargs["url"]  # don't store the URL itself
        super().__init__(*args, **kwargs)

    id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=True, index=True, unique=True)
    domain = db.Column(db.String)
    earliest_crawled_at = db.Column(db.TIMESTAMP(timezone=True))
    latest_crawled_at = db.Column(db.TIMESTAMP(timezone=True))
    crawl_status = db.Column(db.Integer)
    crawler_version = db.Column(db.String)

    @abstractmethod
    def _make_request(self, url):
        pass

    @property
    def error_message(self):
        return self.ERROR_MESSAGES.get(self.crawl_status, "Unknown error")

    def crawl(self, url):
        backoff = self.BACKOFFS.get(self.crawl_status)
        now = datetime.now(tz=UTC)
        if backoff and self.latest_crawled_at + backoff > now:
            raise RecipeURL.BackoffException()

        try:
            response = self._make_request(url)
        except httpx.TimeoutException:
            response = httpx.Response(status_code=598)

        if response.is_success:
            metadata = response.json().get("metadata", {})
            self.crawler_version = metadata.get("service_version")

        self.crawl_status = response.status_code
        self.earliest_crawled_at = self.earliest_crawled_at or now
        self.latest_crawled_at = now
        return response


class CrawlURL(BaseURL):
    __tablename__ = "crawl_urls"

    resolves_to = db.Column(db.String, index=True)
    resolved_id = db.Column(db.String, index=True)
    resolved_domain = db.Column(db.String)

    def __init__(self, *args, **kwargs):
        if "resolves_to" in kwargs:
            kwargs["resolved_id"] = BaseURL.url_to_id(kwargs["resolves_to"])
            kwargs["resolved_domain"] = urlparse(kwargs["resolves_to"]).netloc
            del kwargs["resolves_to"]  # don't store the resolved URL itself
        super().__init__(*args, **kwargs)

    def _make_request(self, url):
        assert BaseURL.url_to_id(url) == self.id

        response = httpx.post(url="http://crawler-service/resolve", data={"url": url})
        if response.is_success:
            self.resolves_to = response.json()["url"]["resolves_to"]
            self.resolved_id = BaseURL.url_to_id(self.resolves_to)
            self.resolved_domain = urlparse(self.resolves_to).netloc
        return response

    @staticmethod
    def find_earliest_crawl(url_id):
        earliest_crawl = (
            db.session.query(CrawlURL).filter_by(resolved_id=url_id).cte(recursive=True)
        )

        previous_step = db.aliased(earliest_crawl)
        earliest_crawl = earliest_crawl.union(
            db.session.query(CrawlURL).filter_by(resolved_id=previous_step.c.id)
        )

        return (
            db.session.query(earliest_crawl)
            .order_by(earliest_crawl.c.earliest_crawled_at.asc())
            .first()
        )

    @staticmethod
    def find_latest_crawl(url_id):
        latest_crawl = (
            db.session.query(CrawlURL).filter_by(id=url_id).cte(recursive=True)
        )

        previous_step = db.aliased(latest_crawl)
        latest_crawl = latest_crawl.union(
            db.session.query(CrawlURL).filter_by(id=previous_step.c.resolved_id)
        )

        return (
            db.session.query(latest_crawl)
            .order_by(latest_crawl.c.latest_crawled_at.desc())
            .first()
        )


class RecipeURL(BaseURL):
    __tablename__ = "recipe_urls"

    recipe_scrapers_version = db.Column(db.String)

    def _make_request(self, url):
        assert BaseURL.url_to_id(url) == self.id

        response = httpx.post(
            url="http://crawler-service/crawl",
            data={"url": url},
            timeout=10.0,
        )
        if response.is_success:
            metadata = response.json().get("metadata", {})
            self.recipe_scrapers_version = metadata["recipe_scrapers_version"]
        return response
