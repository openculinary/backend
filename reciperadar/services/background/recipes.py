import io
from PIL import Image
import os
import requests

from reciperadar.models.recipe import Recipe, RecipeIngredient
from reciperadar.services.background.broker import celery
from reciperadar.services.database import Database


@celery.task
def process_ingredient(recipe_id, ingredient_id):
    session = Database().get_session()
    key = (recipe_id, ingredient_id)
    ingredient = session.query(RecipeIngredient).get(key)
    if not ingredient:
        return

    ingredient_parser_uri = os.environ['INGREDIENT_PARSER_URI']
    parsed_ingredient = requests.get(
        url='{}/parse'.format(ingredient_parser_uri),
        params={'ingredient': ingredient.ingredient}
    ).json()

    if 'name' in parsed_ingredient:
        ingredient.product = parsed_ingredient['name']
    if 'qty' in parsed_ingredient:
        ingredient.quantity = parsed_ingredient['qty']
    if 'unit' in parsed_ingredient:
        ingredient.units = parsed_ingredient['unit']
    session.commit()


@celery.task
def process_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return

    for ingredient in recipe.ingredients:
        process_ingredient.delay(recipe.id, ingredient.id)

    if recipe.image:
        image = requests.get(recipe.image)
        if image.status_code == 200:
            path = 'reciperadar/static/images/recipes/{}'.format(recipe_id[:2])
            os.makedirs(path, exist_ok=True)
            image = Image.open(io.BytesIO(image.content))
            image.save('{}/{}.webp'.format(path, recipe_id), 'webp')
