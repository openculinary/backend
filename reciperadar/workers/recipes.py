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
        response = recipe_url.crawl()
    except RecipeURL.BackoffException:
        print(f'Backoff: {recipe_url.error_message} for url={url}')
        return
    except Exception:
        print(f'{recipe_url.error_message} for url={url}')
        return
    finally:
        session.add(recipe_url)
        session.commit()
        session.close()

    if not response.ok:
        return

    try:
        recipe = Recipe.from_doc(response.json())
    except Exception as e:
        print(f'Failed to load crawler result for url={url} - {e}')
        return

    recipe_id = recipe.id

    session = Database().get_session()
    session.query(Recipe).filter_by(id=recipe_id).delete()
    session.add(recipe)
    session.commit()
    session.close()

    process_recipe.delay(recipe_id)


@celery.task(queue='crawl_url')
def crawl_url(url):
    session = Database().get_session()
    crawl_url = session.query(CrawlURL).get(url) or CrawlURL(url=url)

    try:
        response = crawl_url.crawl()
        url = crawl_url.resolves_to
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

    if not response.ok:
        return

    session = Database().get_session()
    recipe_url = session.query(RecipeURL).get(url) or RecipeURL(url=url)
    session.add(recipe_url)
    session.commit()
    session.close()

    crawl_recipe.delay(url)
