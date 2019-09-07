import io
from PIL import Image
import os
import requests

from reciperadar.models.recipe import Recipe
from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


@celery.task(queue='index_recipe')
def index_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        print('Could not find recipe to index')
        return
    recipe.index()
    print(f'Indexed {recipe.id}')
    session.close()


def save_recipe_image(recipe):
    if not recipe.image:
        return

    dir_path = 'reciperadar/static/images/recipes/{}'.format(recipe.id[:2])
    img_path = '{}/{}.webp'.format(dir_path, recipe.id)
    if not os.path.exists(img_path):
        image = requests.get(recipe.image, timeout=0.25)
        image.raise_for_status()
        os.makedirs(dir_path, exist_ok=True)
        image = Image.open(io.BytesIO(image.content))
        image.save(img_path, 'webp')
        recipe.image = img_path.replace('reciperadar/static/', '')


@celery.task(queue='process_recipe')
def process_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        session.close()
        print('Could not find recipe to process')
        return

    try:
        save_recipe_image(recipe)
    except Exception as e:
        print(e)
        session.close()
        return
    if not recipe.image:
        session.close()
        print(f'No recipe image to index for recipe {recipe.id}')
        return

    session.commit()
    session.close()
    index_recipe.delay(recipe_id)


@celery.task(queue='crawl_recipe')
def crawl_recipe(url, image_url):
    crawler_url = 'http://localhost:6000'
    crawler_data = {
        'url': url,
        'image_url': image_url
    }
    crawler_response = requests.post(url=crawler_url, data=crawler_data)

    if crawler_response.status_code == 429:
        print(f'* Crawler rate-limit exceeded for url={url}')
        return

    if crawler_response.status_code == 501:
        print(f'* Website not supported for url={url}')
        return

    if crawler_response.status_code >= 500:
        print(f'* Scraper failure for url={url}')
        return

    recipe = Recipe.from_doc(crawler_response.json())
    process_recipe.delay(recipe.id)

    session = Database().get_session()
    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()
    session.close()
