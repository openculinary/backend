import pytest
import responses

from reciperadar.models.url import CrawlURL, RecipeURL


@pytest.fixture
def origin_url():
    return 'https://recipe.subdomain.example.com/recipe/123'


@pytest.fixture
def content_url(origin_url):
    return origin_url.replace('subdomain', 'migrated')


def test_origin_url_domain(origin_url):
    url = CrawlURL(url=origin_url)

    assert url.domain == 'example.com'


@responses.activate
def test_origin_url_resolution(origin_url, content_url):
    redir_headers = {'Location': content_url}
    responses.add(responses.GET, origin_url, status=301, headers=redir_headers)
    responses.add(responses.GET, content_url, status=200)

    crawl_url = CrawlURL(url=origin_url)
    recipe_url = crawl_url.crawl()

    assert (crawl_url.url, recipe_url.url) == (origin_url, content_url)
    assert crawl_url.resolves_to == recipe_url.url


def test_content_url_domain(content_url):
    url = RecipeURL(url=content_url)

    assert url.domain == 'example.com'
