from flask import jsonify, request

from reciperadar.app import app
from reciperadar.models.course import Course
from reciperadar.models.ingredient import Ingredient
from reciperadar.models.recipe import Recipe


@app.route('/api/courses')
def courses():
    prefix = request.args.get('pre')
    results = Course().autosuggest(prefix)
    return jsonify([result['name'] for result in results])


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    results = Ingredient().autosuggest(prefix)
    return jsonify([result['name'] for result in results])


@app.route('/api/recipes/search')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    results = Recipe().search(include, exclude, secondary=True)
    return jsonify(results)
