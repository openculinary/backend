from flask import abort, jsonify

from reciperadar import app
from reciperadar.models.recipe import Recipe


@app.route('/api/recipes/<recipe_id>/view')
def recipe(recipe_id):
    recipe = Recipe().get_by_id(recipe_id)
    if not recipe:
        return abort(404)

    results = {
        'total': 1,
        'results': [recipe.to_dict()],
    }
    return jsonify(results)
