from flask import abort, jsonify, request

from reciperadar import app
from reciperadar.models.recipes import Recipe
from reciperadar.workers.recipes import crawl_url, index_recipe


@app.route('/api/recipes/<recipe_id>')
def recipe_get(recipe_id):
    recipe = Recipe().get_by_id(recipe_id)
    if not recipe:
        return abort(404)
    return jsonify(recipe.to_doc())


@app.route('/api/recipes/<recipe_id>/diagnostics')
def recipe_diagnostics(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return abort(404)

    recipe_url = recipe.recipe_url
    earliest_crawl = recipe_url.find_earliest_crawl()

    return jsonify({
        'id': recipe.id,
        'indexed_at': recipe.indexed_at,
        'current_crawl': {
            'url': recipe_url.url,
            'crawled_at': recipe_url.crawled_at,
            'crawl_status': recipe_url.crawl_status,
            'crawler_version': recipe_url.crawler_version,
            'recipe_scrapers_version': recipe_url.recipe_scrapers_version,
        },
        'earliest_crawl': {
            'url': earliest_crawl.url,
            'crawled_at': earliest_crawl.crawled_at,
            'crawl_status': recipe_url.crawl_status,
            'crawler_version': recipe_url.crawler_version,
        },
    })


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
