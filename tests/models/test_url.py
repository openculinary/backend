import pytest
import requests
from unittest.mock import patch

from datetime import datetime

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


def test_crawl_url_timeline(db_session):
    path = [
        (datetime(2020, 1, 1), 'A', 'B'),
        (datetime(2020, 2, 1), 'X', 'Y'),
        (datetime(2020, 2, 1), 'B', 'C'),
        (datetime(2020, 3, 1), 'Y', 'C'),
        (datetime(2020, 3, 1), 'C', 'D'),
        (datetime(2020, 4, 1), 'D', 'D'),
    ]
    path = [
        CrawlURL(url=from_url, resolves_to=to_url, crawled_at=time)
        for (time, from_url, to_url) in path
    ]
    for step in path:
        db_session.add(step)

    recipe = RecipeURL(url='C')
    earliest_crawl = recipe.find_earliest_crawl()
    latest_crawl = recipe.find_latest_crawl()

    assert earliest_crawl.url == 'A'
    assert latest_crawl.resolves_to == 'D'
