from flask import jsonify, request

from reciperadar import app
from reciperadar.models.ingredient import Ingredient
from reciperadar.models.recipe import Recipe


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    results = Ingredient().autosuggest(prefix)
    return jsonify([result['name'] for result in results])


@app.route('/api/recipes/search')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=10)
    results = Recipe().search(include, exclude, offset, limit)
    return jsonify(results)
