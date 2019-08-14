from flask import jsonify, request
from flask_jsonschema import validate

from reciperadar import app
from reciperadar.models.recipe import Recipe
from reciperadar.services.database import Database
from reciperadar.workers.recipes import process_recipe


@app.route('/api/recipes/ingest', methods=['POST'])
@validate('recipes', 'ingest')
def recipe_ingest():
    data = request.get_json()
    recipe = Recipe.from_dict(data)

    session = Database().get_session()
    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()

    process_recipe.delay(recipe.id)
    response = recipe.to_dict()

    session.close()
    return jsonify(response)
