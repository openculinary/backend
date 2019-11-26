from flask import jsonify, request

from reciperadar import app
from reciperadar.models.events.search import SearchEvent
from reciperadar.models.recipes import (
    Recipe,
    RecipeEquipment,
    RecipeIngredient,
)
from reciperadar.workers.events import store_event
from reciperadar.workers.searches import recrawl_search


@app.route('/api/equipment')
def equipment():
    prefix = request.args.get('pre')
    results = RecipeEquipment().autosuggest(prefix)
    return jsonify(results)


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    results = RecipeIngredient().autosuggest(prefix)
    return jsonify(results)


def is_robot(user_agent):
    return user_agent and 'www.uptimerobot.com' in user_agent


@app.route('/api/recipes/search')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    equipment = request.args.getlist('equipment[]')
    offset = min(request.args.get('offset', type=int, default=0), (50*10)-10)
    limit = min(request.args.get('limit', type=int, default=10), 10)
    sort = request.args.get('sort')
    results = Recipe().search(include, exclude, equipment, offset, limit, sort)

    user_agent = request.headers.get('user-agent')
    if not is_robot(user_agent):

        # Perform a recrawl for the search to find any new/missing recipes
        recrawl_search.delay(include)

        # TODO: Once 'event' is json serializable: switch to store_event.delay
        store_event(SearchEvent(
            include=include,
            exclude=exclude,
            equipment=equipment,
            offset=offset,
            limit=limit,
            sort=sort,
            results_ids=[result['id'] for result in results['results']],
            results_total=results['total']
        ))

    return jsonify(results)
