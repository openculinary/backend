from datetime import datetime, timedelta
import io
from PIL import Image
import os
import requests

from reciperadar.models.recipes import Recipe
from reciperadar.models.url import RecipeURL
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
    recipe.indexed_at = datetime.utcnow()
    print(f'Indexed {recipe.id}')

    session.commit()
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


thresholds = {
    200: timedelta(days=28),
    404: timedelta(days=28),
    429: timedelta(hours=1),
    500: timedelta(days=2),
    501: timedelta(days=28),
}


@celery.task(queue='crawl_recipe')
def crawl_recipe(url, image_url):
    session = Database().get_session()
    recipe_url = session.query(RecipeURL).filter(RecipeURL.url == url).first()

    if not recipe_url:
        recipe_url = RecipeURL(url=url)

    if recipe_url.crawled_at:
        threshold = thresholds.get(recipe_url.crawl_status, timedelta(days=1))
        if (recipe_url.crawled_at + threshold) > datetime.utcnow():
            print(f'* Skipping recently crawled url={url}')
            session.close()
            return

    crawler_url = 'http://localhost:6000'
    crawler_response = requests.post(url=crawler_url, data={'url': url})

    recipe_url.crawled_at = datetime.utcnow()
    recipe_url.crawl_status = crawler_response.status_code
    session.add(recipe_url)
    session.commit()

    if crawler_response.status_code == 404:
        print(f'* Crawler did not find a complete recipe for url={url}')
        session.close()
        return

    if crawler_response.status_code == 429:
        print(f'* Crawler rate-limit exceeded for url={url}')
        session.close()
        return

    if crawler_response.status_code == 501:
        print(f'* Website not supported for url={url}')
        session.close()
        return

    if crawler_response.status_code >= 500:
        print(f'* Scraper failure for url={url}')
        session.close()
        return

    recipe = Recipe.from_doc(crawler_response.json())
    process_recipe.delay(recipe.id)

    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()
    session.close()
