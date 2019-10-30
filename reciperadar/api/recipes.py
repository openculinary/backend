from flask import abort, jsonify, request

from reciperadar import app
from reciperadar.models.recipes import Recipe
from reciperadar.services.database import Database
from reciperadar.utils.decorators import internal
from reciperadar.workers.recipes import crawl_recipe, index_recipe


@app.route('/api/recipes/<recipe_id>')
@internal
def recipe_get(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        session.close()
        return abort(404)

    response = recipe.to_doc()
    session.close()

    return jsonify(response)


@app.route('/api/recipes/crawl', methods=['POST'])
@internal
def recipe_crawl():
    url = request.form.get('url')
    if not url:
        return abort(400)

    crawl_recipe.delay(url)
    return jsonify({})


@app.route('/api/recipes/index', methods=['POST'])
@internal
def recipe_index():
    recipe_id = request.form.get('recipe_id')
    if not recipe_id:
        return abort(400)

    index_recipe.delay(recipe_id)
    return jsonify({})
