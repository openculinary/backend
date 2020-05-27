from flask import abort, jsonify, request

from reciperadar import app
from reciperadar.workers.recipes import crawl_url, index_recipe


@app.route('/api/recipes/crawl', methods=['POST'])
def recipe_crawl():
    url = request.form.get('url')
    if not url:
        return abort(400)

    crawl_url.delay(url)
    return jsonify({})


@app.route('/api/recipes/index', methods=['POST'])
def recipe_index():
    recipe_id = request.form.get('recipe_id')
    if not recipe_id:
        return abort(400)

    index_recipe.delay(recipe_id)
    return jsonify({})
