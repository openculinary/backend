from flask import jsonify, request

from reciperadar.app import app, jsonschema
from reciperadar.models.recipe import Recipe
from reciperadar.services.background.recipes import process_recipe
from reciperadar.services.database import Database


@app.route('/api/recipes/ingest', methods=['POST'])
@jsonschema.validate('recipes', 'ingest')
def recipe_ingest():
    data = request.get_json()
    recipe = Recipe.from_json(data)

    session = Database().get_session()
    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()

    process_recipe.delay(recipe.id)
    response = recipe.to_dict()

    session.close()
    return jsonify(response)
