import pytest
import responses

from reciperadar.models.url import CrawlURL, RecipeURL


@pytest.fixture
def crawl_url():
    return 'https://recipe.subdomain.example.com/recipe/123'


@pytest.fixture
def crawl_headers(recipe_url):
    return {'Location': recipe_url}


@pytest.fixture
def recipe_url(crawl_url):
    return crawl_url.replace('subdomain', 'migrated')


def test_crawl_url_domain(crawl_url):
    url = CrawlURL(url=crawl_url)

    assert url.domain == 'example.com'


@responses.activate
def test_crawl_url_resolution(crawl_url, crawl_headers, recipe_url):
    responses.add(responses.GET, crawl_url, status=301, headers=crawl_headers)
    responses.add(responses.GET, recipe_url, status=200)

    crawl_input = CrawlURL(url=crawl_url)
    crawl_output = crawl_input.crawl()

    assert (crawl_input.url, crawl_output.url) == (crawl_url, recipe_url)


def test_recipe_url_domain(recipe_url):
    url = RecipeURL(url=recipe_url)

    assert url.domain == 'example.com'
