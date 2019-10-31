from reciperadar import app
from reciperadar.utils.decorators import internal


@app.route('/test/internal')
@internal
def internal_route():
    return '', 200


def test_external_request_denied(client):
    headers = {'X-RecipeRadar-External': True}
    response = client.get('/test/internal', headers=headers)

    assert response.status_code == 403


def test_internal_request_allowed(client):
    headers = {}
    response = client.get('/test/internal', headers=headers)

    assert response.status_code == 200
