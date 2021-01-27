import responses
from unittest.mock import call, patch

from reciperadar.models.url import RecipeURL
from reciperadar.workers.recipes import crawl_url


def set_resolution(url):
    responses.add(responses.POST, 'http://crawler-service/resolve', json={
        'url': {'resolves_to': url}
    })


@responses.activate
@patch('reciperadar.workers.recipes.crawl_recipe.delay')
def test_crawl_url_samedomain(crawl_recipe, db_session):
    origin_url = '//example.com/A'
    current_url = '//example.com/B'

    set_resolution(current_url)
    crawl_url(origin_url)

    assert call(current_url) in crawl_recipe.call_args_list


@responses.activate
@patch('reciperadar.workers.recipes.crawl_recipe.delay')
def test_crawl_unseen_crossdomain(crawl_recipe, db_session):
    origin_url = '//example.org/A'
    current_url = '//example.com/B'

    set_resolution(current_url)
    crawl_url(origin_url)

    assert call(current_url) in crawl_recipe.call_args_list


@responses.activate
@patch('reciperadar.workers.recipes.crawl_recipe.delay')
def test_crawl_seen_crossdomain(crawl_recipe, db_session):
    origin_url = '//example.org/A'
    current_url = '//example.com/B'

    existing_recipe = RecipeURL(url=current_url)
    db_session.add(existing_recipe)

    set_resolution(current_url)
    crawl_url(origin_url)

    assert crawl_recipe.called is False
