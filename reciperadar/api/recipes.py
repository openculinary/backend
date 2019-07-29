from flask import jsonify, request

from reciperadar import app, jsonschema
from reciperadar.models.recipe import Recipe, RecipeIngredient
from reciperadar.services.database import Database
from reciperadar.workers.recipes import process_recipe


@app.route('/api/recipes/ingest', methods=['POST'])
@jsonschema.validate('recipes', 'ingest')
def recipe_ingest():
    data = request.get_json()
    recipe = Recipe.from_dict(data)

    session = Database().get_session()
    session.query(RecipeIngredient).filter_by(recipe_id=recipe.id).delete()
    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()

    process_recipe.delay(recipe.id)
    response = recipe.to_dict()

    session.close()
    return jsonify(response)
