from flask import abort, redirect

from reciperadar import app
from reciperadar.models.recipe import Recipe
from reciperadar.services.database import Database


@app.route('/api/redirect/recipe/<recipe_id>')
def recipe_redirect(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return abort(404)
    session.close()
    return redirect(recipe.src, code=301)
