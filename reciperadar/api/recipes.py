from flask import jsonify, request

from reciperadar import app
from reciperadar.workers.recipes import crawl_recipe


@app.route('/api/recipes/crawl', methods=['POST'])
def recipe_crawl():
    url = request.form.get('url')
    image_url = request.form.get('image_url')

    crawl_recipe.delay(url, image_url)
    return jsonify({})
