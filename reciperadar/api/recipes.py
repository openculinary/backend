from flask import abort, jsonify, request

from reciperadar import app
from reciperadar.models.recipes import Recipe
from reciperadar.workers.recipes import crawl_url, index_recipe


@app.route('/recipes/<recipe_id>')
def recipe_get(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return abort(404)
    return jsonify(recipe.to_doc())


@app.route('/recipes/<recipe_id>/diagnostics')
def recipe_diagnostics(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return abort(404)

    recipe_url = recipe.recipe_url
    earliest_crawl = recipe_url.find_earliest_crawl()

    return jsonify({
        'id': recipe.id,
        'indexed_at': recipe.indexed_at,
        'latest_crawl': {
            'url': recipe_url.url,
            'crawled_at': recipe_url.crawled_at,
            'crawl_status': recipe_url.crawl_status,
            'crawler_version': recipe_url.crawler_version,
            'recipe_scrapers_version': recipe_url.recipe_scrapers_version,
        },
        'earliest_crawl': {
            'url': earliest_crawl.url,
            'crawled_at': earliest_crawl.crawled_at,
            'crawl_status': earliest_crawl.crawl_status,
            'crawler_version': earliest_crawl.crawler_version,
        },
    })


@app.route('/recipes/<recipe_id>/crawl')
def recipe_crawl_retrieve(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return abort(404)

    recipe_data = recipe.recipe_url.crawl().json()['recipe']
    recipe = Recipe.from_doc(recipe_data)
    return jsonify()


@app.route('/recipes/crawl', methods=['POST'])
def recipe_crawl_submit():
    url = request.form.get('url')
    if not url:
        return abort(400)

    crawl_url.delay(url)
    return jsonify({})


@app.route('/recipes/index', methods=['POST'])
def recipe_index():
    recipe_id = request.form.get('recipe_id')
    if not recipe_id:
        return abort(400)

    index_recipe.delay(recipe_id)
    return jsonify({})
