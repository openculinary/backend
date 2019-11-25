from reciperadar.models.recipes import Recipe
from reciperadar.models.url import CrawlURL, RecipeURL
from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


@celery.task(queue='index_recipe')
def index_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        print('Could not find recipe to index')
        session.close()
        return

    if recipe.index():
        print(f'Indexed {recipe.id} for url={recipe.src}')
        session.commit()

    session.close()


@celery.task(queue='process_recipe')
def process_recipe(recipe_id):
    session = Database().get_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        print('Could not find recipe to process')
        session.close()
        return

    index_recipe.delay(recipe.id)
    session.close()


@celery.task(queue='crawl_recipe')
def crawl_recipe(url):
    session = Database().get_session()
    recipe_url = session.query(RecipeURL).get(url) or RecipeURL(url=url)

    try:
        recipe_json = recipe_url.crawl().json()
    except RecipeURL.BackoffException:
        print(f'Backoff: {recipe_url.error_message} for url={recipe_url.url}')
        return
    except Exception:
        print(f'{recipe_url.error_message} for url={recipe_url.url}')
        return
    finally:
        session.add(recipe_url)
        session.commit()
        session.close()

    recipe = Recipe.from_doc(recipe_json)
    process_recipe.delay(recipe.id)

    session = Database().get_session()
    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()
    session.close()


@celery.task(queue='crawl_url')
def crawl_url(url):
    session = Database().get_session()
    crawl_url = session.query(CrawlURL).get(url) or CrawlURL(url=url)

    try:
        response = crawl_url.crawl()
    except RecipeURL.BackoffException:
        print(f'Backoff: {crawl_url.error_message} for url={crawl_url.url}')
        return
    except Exception:
        print(f'{crawl_url.error_message} for url={crawl_url.url}')
        return
    finally:
        session.add(crawl_url)
        session.commit()
        session.close()

    recipe_url = RecipeURL(response.url)
    crawl_recipe.delay(recipe_url.url)

    session = Database().get_session()
    session.query(RecipeURL).get(recipe_url.url).delete()
    session.add(recipe_url)
    session.commit()
    session.close()
