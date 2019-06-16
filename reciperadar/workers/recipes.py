from fractions import Fraction
import io
from PIL import Image
import os
import requests

from reciperadar.models.recipe import Recipe, RecipeIngredient
from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


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
        quantity_fragments = parsed_ingredient['qty'].split()
        quantity = float(sum(Fraction(f) for f in quantity_fragments))
        ingredient.quantity = quantity
    if 'unit' in parsed_ingredient:
        ingredient.units = parsed_ingredient['unit']
    session.commit()
    session.close()


@celery.task
def index_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return
    recipe.index()


@celery.task
def process_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return

    for ingredient in recipe.ingredients:
        process_ingredient.delay(recipe.id, ingredient.id)

    if recipe.image:
        dir_path = 'reciperadar/static/images/recipes/{}'.format(recipe_id[:2])
        img_path = '{}/{}.webp'.format(dir_path, recipe_id)
        if not os.path.exists(img_path):
            image = requests.get(recipe.image)
            try:
                image.raise_for_status()
            except Exception:
                return

            os.makedirs(dir_path, exist_ok=True)
            image = Image.open(io.BytesIO(image.content))
            image.save(img_path, 'webp')
            recipe.image = img_path.replace('reciperadar/static/', '')
            session.commit()

    index_recipe.delay(recipe_id)
    session.close()
