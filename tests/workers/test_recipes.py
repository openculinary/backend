import pytest
from unittest.mock import call, patch

from reciperadar.models.url import RecipeURL
from reciperadar.workers.recipes import crawl_url


def set_resolution(respx_mock, url):
    respx_mock.post("/resolve").respond(json={"url": {"resolves_to": url}})


@patch("reciperadar.workers.recipes.crawl_recipe.delay")
@pytest.mark.respx(
    base_url="http://crawler-service", assert_all_called=True, using="httpx"
)
def test_crawl_url_samedomain(crawl_recipe, respx_mock, db_session):
    origin_url = "//example.test/A"
    current_url = "//example.test/B"

    set_resolution(respx_mock, current_url)
    crawl_url(origin_url)

    assert call(current_url) in crawl_recipe.call_args_list


@patch("reciperadar.workers.recipes.crawl_recipe.delay")
@pytest.mark.respx(
    base_url="http://crawler-service", assert_all_called=True, using="httpx"
)
def test_crawl_unseen_crossdomain(crawl_recipe, respx_mock, db_session):
    origin_url = "//example.test/A"
    current_url = "//example.test/B"

    set_resolution(respx_mock, current_url)
    crawl_url(origin_url)

    assert call(current_url) in crawl_recipe.call_args_list


@patch("reciperadar.workers.recipes.crawl_recipe.delay")
@pytest.mark.respx(
    base_url="http://crawler-service", assert_all_called=True, using="httpx"
)
def test_crawl_seen_crossdomain(crawl_recipe, respx_mock, db_session):
    origin_url = "//example.original.test/A"
    current_url = "//example.updated.test/B"

    existing_recipe = RecipeURL(url=current_url)
    db_session.add(existing_recipe)
    del existing_recipe

    set_resolution(respx_mock, current_url)
    crawl_url(origin_url)

    assert crawl_recipe.called is False
