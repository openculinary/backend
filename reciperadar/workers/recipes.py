from fractions import Fraction
import io
from PIL import Image
import os
import requests
from unicodedata import numeric

from reciperadar.models.recipe import Recipe
from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


def process_ingredients(recipe):
    ingredients_by_desc = {}
    for ingredient in recipe.ingredients:
        ingredients_by_desc[ingredient.ingredient] = ingredient

    tagger_uri = os.environ['INGREDIENT_PARSER_URI']
    parsed_ingredients = requests.get(
        url='{}/parse'.format(tagger_uri),
        params={'ingredients[]': [i.ingredient for i in recipe.ingredients]}
    ).json()

    for parsed_ingredient in parsed_ingredients:
        input_desc = parsed_ingredient['input']
        ingredient = ingredients_by_desc.get(input_desc)
        if ingredient is None:
            continue
        if 'name' in parsed_ingredient:
            ingredient.product = parsed_ingredient['name']
        if 'qty' in parsed_ingredient:
            ingredient.quantity = 0
            fragments = parsed_ingredient['qty'].split()
            for fragment in fragments:
                if len(fragment) == 1:
                    fragment = numeric(fragment)
                elif fragment[-1].isdigit():
                    fragment = Fraction(fragment)
                else:
                    fragment = Fraction(fragment[:-1]) + numeric(fragment[-1])
                ingredient.quantity += float(fragment)
        if 'unit' in parsed_ingredient:
            ingredient.units = parsed_ingredient['unit']


@celery.task
def index_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return

    process_ingredients(recipe)
    if all([ingredient.product for ingredient in recipe.ingredients]):
        recipe.index()
        print(f'Indexed {recipe.id}')

    session.add(recipe)
    session.commit()
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
