from mock import patch

from reciperadar.models.recipes import Recipe


@patch('werkzeug.datastructures.Headers.get')
@patch('reciperadar.api.search.recrawl_search.delay')
@patch('reciperadar.api.search.store_event')
@patch.object(Recipe, 'search')
def test_search_user_agent_optional(search, store, recrawl, get, client):
    search.return_value = {'results': [], 'total': 0}
    get.return_value = None

    response = client.get('/api/recipes/search', headers={'user-agent': None})

    assert response.status_code == 200


@patch('reciperadar.api.search.recrawl_search.delay')
@patch('reciperadar.api.search.store_event')
@patch.object(Recipe, 'search')
def test_search_recrawling(search, store, recrawl, client):
    search.return_value = {'results': [], 'total': 0}

    response = client.get('/api/recipes/search', headers={'user-agent': None})

    assert response.status_code == 200
    assert recrawl.called is True


@patch('reciperadar.api.search.recrawl_search.delay')
@patch('reciperadar.api.search.store_event')
@patch.object(Recipe, 'search')
def test_bot_search(search, store, recrawl, client):
    search.return_value = {'results': [], 'total': 0}

    user_agent = (
        'Mozilla/5.0+',
        '(compatible; UptimeRobot/2.0; http://www.uptimerobot.com/)'
    )
    client.get('/api/recipes/search', headers={'user-agent': user_agent})

    assert store.called
    assert store.call_args[0][0].suspected_bot
