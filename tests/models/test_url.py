import pytest
import requests
from unittest.mock import patch

from reciperadar.models.url import CrawlURL, RecipeURL


@pytest.fixture
def origin_url():
    return 'https://recipe.subdomain.example.com/recipe/123'


@pytest.fixture
def content_url(origin_url):
    return origin_url.replace('subdomain', 'migrated')


@patch('requests.post')
def test_crawl_timeout(post, origin_url):
    post.side_effect = [requests.exceptions.Timeout]

    url = CrawlURL(url=origin_url)
    url.crawl()

    assert url.crawl_status == 598
    assert 'timeout' in url.error_message


def test_origin_url_domain(origin_url):
    url = CrawlURL(url=origin_url)

    assert url.domain == 'example.com'


def test_content_url_domain(content_url):
    url = RecipeURL(url=content_url)

    assert url.domain == 'example.com'


def test_crawl_url_session(db_session, origin_url):
    url = CrawlURL(url=origin_url)
    db_session.add(url)
    db_session.commit()
    assert CrawlURL.query.count() == 1


def test_crawl_url_session_reset(db_session):
    assert CrawlURL.query.count() == 0
