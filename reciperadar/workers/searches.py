import httpx

from reciperadar import db
from reciperadar.workers.broker import celery


@celery.task(queue="recrawl_search")
def recrawl_search(include, exclude, equipment, dietary_properties, offset):
    params = {
        "include[]": include,
        "exclude[]": exclude,
        "equipment[]": equipment,
        "dietary_properties[]": dietary_properties,
        "offset": offset,
    }

    from reciperadar.models.recipes.product import ProductName

    # Validate the products contained in the query
    query_products = set(include + exclude)
    found_products = db.session.query(
        db.func.count(ProductName.singular.distinct()).filter(
            ProductName.singular.in_(query_products)
        )
    )
    if found_products.scalar() < len(query_products):
        return []

    try:
        response = httpx.post(url="http://recrawler-service", params=params)
        if not response.is_success:
            raise Exception("non-success status code")
        return response.json()
    except Exception as e:
        print(f'Recrawling failed due to "{e.__class__.__name__}" exception')
        return []
