import json

from opensearchpy import OpenSearch
from sqlalchemy.orm import joinedload

from reciperadar.workers.broker import celery


def get_product_synonyms():
    from reciperadar.models.recipes.product import Product

    synonyms = {}
    products = Product.query.options(joinedload(Product.names))
    for product in products:
        if len(product.names) == 1:
            continue
        for synonym in product.singular_names:
            synonyms[synonym] = sorted(product.singular_names)
    return synonyms


def recreate_product_synonym_index(index):
    settings = {"index": {"number_of_replicas": 0}}
    mapping = {"properties": {"synonyms": {"type": "keyword"}}}

    es = OpenSearch("opensearch")
    es.indices.delete(index=index, ignore_unavailable=True)
    es.indices.create(index=index)
    es.indices.put_settings(index=index, body=settings)
    es.indices.put_mapping(index=index, body=mapping)


def populate_product_synonym_index(index, synonyms):
    es = OpenSearch("opensearch")
    actions = []
    for product_name, product_synonyms in synonyms.items():
        actions.append(json.dumps({"index": {"_index": index, "_id": product_name}}))
        actions.append(json.dumps({"synonyms": product_synonyms}))
        if len(actions) % 100 == 0:
            es.bulk("\n".join(actions))
            actions.clear()
    if actions:
        es.bulk("\n".join(actions))
    es.indices.refresh(index=index)


@celery.task(queue="update_product_synonyms")
def update_product_synonyms():
    synonyms = get_product_synonyms()
    print(f"* Found {len(synonyms)} synonym entries to be persisted")
    recreate_product_synonym_index("product_synonyms")
    print("* Recreated product synonym index")
    populate_product_synonym_index("product_synonyms", synonyms)
    print("* Populated product synonym index")
