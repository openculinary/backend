from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

from reciperadar.search import SearchEngine

app = Flask(__name__)


@app.route('/api/courses')
def courses():
    prefix = request.args.get('pre')
    search = SearchEngine()
    results = search.autosuggest('courses', prefix)
    return jsonify(results)


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    search = SearchEngine()
    results = search.autosuggest('ingredients', prefix)
    return jsonify(results)


def format_recipe(doc):
    source = doc.pop('_source')

    title = source.pop('name')
    image = source.pop('image')
    time = source.pop('cookTime', None)
    url = source.pop('url')

    matches = []
    highlights = doc.get('highlight', {}).get('ingredients', [])
    for highlight in highlights:
        bs = BeautifulSoup(highlight)
        matches += [em.text.lower() for em in bs.findAll('em')]
    matches = list(set(matches))

    return {
        'title': title,
        'image': image,
        'time': time,
        'url': url,
        'matches': matches
    }


@app.route('/api/recipes')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    search = SearchEngine()
    results = search.recipe_search(include, exclude)
    results = [format_recipe(result) for result in results]
    return jsonify(results)
