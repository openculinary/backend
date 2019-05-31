from flask import Flask, jsonify, request

from reciperadar.course import Course
from reciperadar.ingredient import Ingredient
from reciperadar.recipe import Recipe

app = Flask(__name__)


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


@app.route('/api/recipes')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    results = Recipe().search(include, exclude)
    return jsonify(results)
