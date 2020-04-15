from mock import patch

from reciperadar.search.recipes import RecipeSearch


@patch.object(RecipeSearch, 'query')
def test_search_invalid_sort(query, client):
    response = client.get(
        path='/api/recipes/search',
        query_string={'sort': 'invalid'}
    )

    assert response.status_code == 400
    assert not query.called


@patch('werkzeug.datastructures.Headers.get')
@patch('reciperadar.api.recipes.recrawl_search.delay')
@patch('reciperadar.api.recipes.store_event')
@patch.object(RecipeSearch, 'query')
def test_search_user_agent_optional(query, store, recrawl, get, client):
    query.return_value = {'results': [], 'total': 0}
    get.return_value = None

    response = client.get('/api/recipes/search', headers={'user-agent': None})

    assert response.status_code == 200


@patch('reciperadar.api.recipes.recrawl_search.delay')
@patch('reciperadar.api.recipes.store_event')
@patch.object(RecipeSearch, 'query')
def test_search_recrawling(query, store, recrawl, client):
    query.return_value = {'results': [], 'total': 0}

    response = client.get('/api/recipes/search', headers={'user-agent': None})

    assert response.status_code == 200
    assert recrawl.called is True


@patch('reciperadar.api.recipes.recrawl_search.delay')
@patch('reciperadar.api.recipes.store_event')
@patch.object(RecipeSearch, 'query')
def test_bot_search(query, store, recrawl, client):
    query.return_value = {'results': [], 'total': 0}

    user_agent = (
        'Mozilla/5.0+',
        '(compatible; UptimeRobot/2.0; http://www.uptimerobot.com/)'
    )
    client.get('/api/recipes/search', headers={'user-agent': user_agent})

    assert store.called
    assert store.call_args[0][0].suspected_bot
