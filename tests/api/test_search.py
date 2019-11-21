from mock import patch

from reciperadar.models.recipes import Recipe


@patch('werkzeug.datastructures.Headers.get')
@patch('reciperadar.api.search.store_event')
@patch.object(Recipe, 'search')
def test_search_user_agent_optional(mock_search, mock_store, mock_get, client):
    mock_search.return_value = {'results': [], 'total': 0}
    mock_get.return_value = None

    response = client.get('/api/recipes/search', headers={'user-agent': None})

    assert response.status_code == 200
