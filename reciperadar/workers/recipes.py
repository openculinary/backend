from elasticsearch.exceptions import ConflictError
from fractions import Fraction
import io
from PIL import Image
import os
import requests
from time import sleep
from unicodedata import numeric

from reciperadar.models.recipe import Recipe, RecipeIngredient
from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


@celery.task
def index_ingredient(recipe_id, ingredient_id, attempt=1):
    if attempt > 3:
        print(f'Failed to index {recipe_id} {ingredient_id}')
        return

    session = Database().get_session()
    key = (recipe_id, ingredient_id)
    ingredient = session.query(RecipeIngredient).get(key)
    if not ingredient:
        return

    try:
        ingredient.index()
    except ConflictError:
        sleep(attempt)
        index_ingredient.delay(recipe_id, ingredient_id, attempt + 1)
    session.close()


@celery.task
def process_ingredient(recipe_id, ingredient_id):
    session = Database().get_session()
    key = (recipe_id, ingredient_id)
    ingredient = session.query(RecipeIngredient).get(key)
    if not ingredient:
        session.close()
        return

    ingredient_parser_uri = os.environ['INGREDIENT_PARSER_URI']
    parsed_ingredient = requests.get(
        url='{}/parse'.format(ingredient_parser_uri),
        params={'ingredient': ingredient.ingredient}
    ).json()

    updated = False
    if 'name' in parsed_ingredient:
        ingredient.product = parsed_ingredient['name']
        updated = True
    if 'qty' in parsed_ingredient:
        ingredient.quantity = 0
        fragments = parsed_ingredient['qty'].split()
        for fragment in fragments:
            if len(fragment) == 1:
                fragment = numeric(fragment)
            elif fragment[-1].isdigit():
                fragment = float(fragment)
            else:
                fragment = float(fragment[i:-1]) + numeric(fragment[-1])
            ingredient.quantity += fragment
        updated = True
    if 'unit' in parsed_ingredient:
        ingredient.units = parsed_ingredient['unit']
        updated = True
    if ingredient.verb is not None:
        updated = True

    if updated:
        index_ingredient.delay(recipe_id, ingredient_id)

    session.commit()
    session.close()


@celery.task
def index_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return

    recipe.index()
    for ingredient in recipe.ingredients:
        process_ingredient.delay(recipe.id, ingredient.id)
    session.close()


def save_recipe_image(recipe):
    if not recipe.image:
        return

    dir_path = 'reciperadar/static/images/recipes/{}'.format(recipe.id[:2])
    img_path = '{}/{}.webp'.format(dir_path, recipe.id)
    if not os.path.exists(img_path):
        image = requests.get(recipe.image)
        image.raise_for_status()
        os.makedirs(dir_path, exist_ok=True)
        image = Image.open(io.BytesIO(image.content))
        image.save(img_path, 'webp')
        recipe.image = img_path.replace('reciperadar/static/', '')


@celery.task
def process_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        session.close()
        return

    try:
        save_recipe_image(recipe)
        session.commit()
    except Exception:
        pass

    index_recipe.delay(recipe_id)
    session.close()
