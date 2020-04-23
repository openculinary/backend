from sqlalchemy.orm import aliased

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


def find_earliest_crawl(session, url):
    earliest_crawl = (
        session.query(
            CrawlURL.crawled_at,
            CrawlURL.url,
            CrawlURL.resolves_to
        )
        .filter_by(resolves_to=url)
        .cte(recursive=True)
    )

    previous_step = aliased(earliest_crawl)
    earliest_crawl = earliest_crawl.union_all(
        session.query(
            CrawlURL.crawled_at,
            CrawlURL.url,
            previous_step.c.url
        )
        .filter_by(resolves_to=previous_step.c.url)
        .filter(CrawlURL.resolves_to != previous_step.c.resolves_to)
    )

    return (
        session.query(earliest_crawl)
        .order_by(earliest_crawl.c.crawled_at.asc())
        .first()
    )


def find_latest_crawl(session, url):
    latest_crawl = (
        session.query(
            CrawlURL.crawled_at,
            CrawlURL.url,
            CrawlURL.resolves_to
        )
        .filter_by(resolves_to=url)
        .cte(recursive=True)
    )

    previous_step = aliased(latest_crawl)
    latest_crawl = latest_crawl.union_all(
        session.query(
            CrawlURL.crawled_at,
            CrawlURL.url,
            previous_step.c.url
        )
        .filter_by(url=previous_step.c.resolves_to)
        .filter(CrawlURL.resolves_to != previous_step.c.resolves_to)
    )

    return (
        session.query(latest_crawl)
        .order_by(latest_crawl.c.crawled_at.desc())
        .first()
    )


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
        recipe_data = response.json()
    except Exception as e:
        print(f'Failed to load crawler result for url={url} - {e}')
        return

    session = Database().get_session()

    '''
    Due to the fluid nature of the world wide web, a vist to a specific URL
    that previously contained recipe contents may result in a redirect to a
    different web address.

    These relocations can occur multiple times, and it's difficult to predict
    the times at which RecipeRadar will crawl the recipe at each address.

    What this ends up creating is a URL redirection graph.  We can only update
    the links in the graph for a URL when we crawl it.

    RecipeRadar makes the assumption that at any given point in time, there
    will only be a single 'destination' (final landing URL) for each recipe.

    Here's an example of a complicated scenario:

    <- past        future ->

      A-----\
             B-----D-----E
       C----------/


    RecipeRadar has learned about the recipe via two different paths, 'A'
    and 'C'.

    Initially 'A' redirected to page 'B', and at the time we crawled it using
    address 'C', the website owner had updated A, B and C to point to an
    updated location 'D'.

    The graph includes one further change made by the website owner, who added 
    a redirect from 'D' to 'E' in order to use a cleaner URL.

    In order to de-duplicate recipes in the RecipeRadar search engine, we use
    the oldest-known-URL for each recipe as the 'source' location, and we
    only include one recipe per source in the search engine.

    We believe the oldest-known-URL will be the most stable source address,
    since it cannot be changed by the website owner, and we have a record of
    it.

    Recipe hyperlinks displayed to users will contain the most-recent-known
    recipe URL.  This should reduce the number of redirects that the user
    has to follow in order to reach the destination, and ensures that they are
    taken to the most up-to-date URL format that we know about.


    To implement this algorithm in code, we first navigate forwards in time
    to find the 'most recent' destination for each input URL.  For example,
    given the graph above, both 'A' and 'C' will navigate forwards to 'E'.
    This is implemented by the `find_latest_crawl` method.

    Once we have our current-best target URL, we then trace backwards in time
    to find the earliest graph node that can reach the target.  We use this as
    our source URL, and this is implemented by the `find_earliest_crawl`
    method.
    '''

    # Find any more-recent crawls of this URL, allowing detection of duplicates
    latest_crawl = find_latest_crawl(session, url)
    if not latest_crawl:
        print(f'Failed to find latest crawl for url={url}')
        return

    # Find the first-known crawl for the latest URL, and consider it the origin
    earliest_crawl = find_earliest_crawl(session, latest_crawl.resolves_to)
    if not earliest_crawl:
        print(f'Failed to find earliest crawl for url={url}')
        return

    recipe_data['src'] = earliest_crawl.url
    recipe_data['dst'] = latest_crawl.resolves_to
    recipe = Recipe.from_doc(recipe_data)

    session.query(Recipe).filter_by(id=recipe.id).delete()
    session.add(recipe)
    session.commit()

    process_recipe.delay(recipe.id)
    session.close()


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
