from flask import jsonify, request

from reciperadar import app
from reciperadar.models.events.search import SearchEvent
from reciperadar.models.recipes import Recipe, RecipeIngredient
from reciperadar.workers.events import store_event


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    results = RecipeIngredient().autosuggest(prefix)
    return jsonify(results)


@app.route('/api/recipes/search')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    offset = min(request.args.get('offset', type=int, default=0), (50*10)-10)
    limit = min(request.args.get('limit', type=int, default=10), 10)
    sort = request.args.get('sort')
    results = Recipe().search(include, exclude, offset, limit, sort)

    store_event(SearchEvent(
        include=include,
        exclude=exclude,
        offset=offset,
        limit=limit,
        sort=sort,
        results_ids=[result['id'] for result in results['results']],
        results_total=results['total']
    ))

    return jsonify(results)
