from pymmh3 import hash_bytes

from reciperadar import db
from reciperadar.models.recipes import Recipe
from reciperadar.models.domain import Domain
from reciperadar.models.url import CrawlURL, RecipeURL
from reciperadar.workers.broker import celery


@celery.task(queue="index_recipe")
def index_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        print("Could not find recipe to index")
        db.session.close()
        return

    # Check whether web crawling is allowed for the domain
    domain = db.session.get(Domain, recipe.domain) or Domain(domain=recipe.domain)
    if domain.crawl_enabled is False:
        print(f"Skipping recipe indexing: not enabled for {recipe.domain}")
        db.session.close()
        return

    # Display only the oldest-known recipe of record; redirect all others to it
    earliest_crawl = CrawlURL.find_earliest_crawl(recipe.dst)
    if earliest_crawl:
        src_hash = hash_bytes(earliest_crawl.url).encode("utf-8")
        earliest_id = Recipe.generate_id(src_hash)
        if recipe.id != earliest_id:
            recipe.redirected_id = earliest_id
            print(f"Redirected {recipe.id} to {earliest_id} url={earliest_crawl.url}")

    if recipe.index():
        print(f"Indexed {recipe.id} for url={recipe.src}")
        db.session.commit()

    db.session.close()


@celery.task(queue="crawl_recipe")
def crawl_recipe(url):
    recipe_url = db.session.get(RecipeURL, url) or RecipeURL(url=url)
    domain = db.session.get(Domain, recipe_url.domain) or Domain(
        domain=recipe_url.domain
    )

    # Check whether web crawling is allowed for the domain
    if domain.crawl_enabled is False:
        print(f"Skipping recipe crawl: not enabled for {recipe_url.domain}")
        db.session.close()
        return

    try:
        response = recipe_url.crawl()
        response.raise_for_status()
    except RecipeURL.BackoffException:
        print(f"Backoff: {recipe_url.error_message} for url={url}")
        return
    except Exception:
        print(f"{recipe_url.error_message} for url={url}")
        return
    finally:
        db.session.add(recipe_url)
        db.session.commit()

    try:
        recipe_data = response.json()["recipe"]
    except Exception as e:
        print(f"Failed to load crawler result for url={url} - {e}")
        db.session.close()
        return

    """
    Due to the fluid nature of the world wide web, a visit to a specific URL
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
    """

    # Find any more-recent crawls of this URL, allowing detection of duplicates
    latest_crawl = CrawlURL.find_latest_crawl(recipe_url.url)
    if not latest_crawl:
        print(f"Failed to find latest crawl for url={url}")
        return

    # Find the first-known crawl for the latest URL, and consider it the origin
    earliest_crawl = CrawlURL.find_earliest_crawl(latest_crawl.resolves_to)
    if not earliest_crawl:
        print(f"Failed to find earliest crawl for url={url}")
        return

    recipe_data["src"] = earliest_crawl.url
    recipe_data["dst"] = latest_crawl.resolves_to
    recipe = Recipe.from_doc(recipe_data)

    domain = db.session.get(Domain, recipe.domain) or Domain(domain=recipe.domain)

    db.session.query(Recipe).filter_by(id=recipe.id).delete()
    db.session.add(recipe)
    db.session.add(domain)

    try:
        db.session.commit()
        index_recipe.delay(recipe.id)
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()


@celery.task(queue="crawl_url")
def crawl_url(url):
    crawl_url = db.session.get(CrawlURL, url) or CrawlURL(url=url)
    domain = db.session.get(Domain, crawl_url.domain) or Domain(domain=crawl_url.domain)

    # Check whether web crawling is allowed for the domain
    if domain.crawl_enabled is False:
        print(f"Skipping URL crawl: not enabled for {crawl_url.domain}")
        db.session.close()
        return

    try:
        response = crawl_url.crawl()
        response.raise_for_status()
        url = crawl_url.resolves_to
    except RecipeURL.BackoffException:
        print(f"Backoff: {crawl_url.error_message} for url={crawl_url.url}")
        return
    except Exception:
        print(f"{crawl_url.error_message} for url={crawl_url.url}")
        return
    finally:
        db.session.add(crawl_url)
        db.session.commit()

    existing_url = db.session.get(RecipeURL, url)

    # Prevent cross-domain URL references from recrawling existing content
    if existing_url and existing_url.domain != crawl_url.domain:
        print(
            "Skipping cross-domain crawl: "
            f"{existing_url.domain} != {crawl_url.domain}"
        )
        db.session.close()
        return

    recipe_url = existing_url or RecipeURL(url=url)
    db.session.add(recipe_url)

    try:
        db.session.commit()
        crawl_recipe.delay(url)
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()
