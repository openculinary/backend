from flask import abort, jsonify, request
from user_agents import parse as ua_parser

from reciperadar import app
from reciperadar.models.events.search import SearchEvent
from reciperadar.models.recipes import Recipe
from reciperadar.search.recipes import RecipeSearch
from reciperadar.utils.decorators import internal
from reciperadar.workers.events import store_event
from reciperadar.workers.recipes import crawl_url, index_recipe
from reciperadar.workers.searches import recrawl_search


@app.route('/api/recipes/<recipe_id>')
@internal
def recipe_get(recipe_id):
    recipe = Recipe().get_by_id(recipe_id)
    if not recipe:
        return abort(404)
    return jsonify(recipe.to_doc())


@app.route('/api/recipes/<recipe_id>/view')
def recipe_view(recipe_id):
    recipe = Recipe().get_by_id(recipe_id)
    if not recipe:
        return abort(404)

    results = {
        'total': 1,
        'results': [recipe.to_dict()],
    }
    return jsonify(results)


@app.route('/api/recipes/search')
def recipe_search():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    equipment = request.args.getlist('equipment[]')
    offset = min(request.args.get('offset', type=int, default=0), (25*10)-10)
    limit = min(request.args.get('limit', type=int, default=10), 10)
    sort = request.args.get('sort', type=str)

    if sort and sort not in RecipeSearch.sort_methods():
        return abort(400)

    results = RecipeSearch().query(
        include=include,
        exclude=exclude,
        equipment=equipment,
        offset=offset,
        limit=limit,
        sort=sort
    )

    user_agent = request.headers.get('user-agent')
    suspected_bot = ua_parser(user_agent or '').is_bot

    # Perform a recrawl for the search to find any new/missing recipes
    recrawl_search.delay(include, exclude, equipment, offset)

    # TODO: Once 'event' is json serializable: switch to store_event.delay
    store_event(SearchEvent(
        suspected_bot=suspected_bot,
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


@app.route('/api/recipes/crawl', methods=['POST'])
@internal
def recipe_crawl():
    url = request.form.get('url')
    if not url:
        return abort(400)

    crawl_url.delay(url)
    return jsonify({})


@app.route('/api/recipes/index', methods=['POST'])
@internal
def recipe_index():
    recipe_id = request.form.get('recipe_id')
    if not recipe_id:
        return abort(400)

    index_recipe.delay(recipe_id)
    return jsonify({})
