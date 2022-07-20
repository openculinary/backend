import json

from elasticsearch import Elasticsearch
from sqlalchemy.orm import joinedload

from reciperadar.models.recipes.product import Product
from reciperadar.workers.broker import celery


def get_product_synonyms():
    synonyms = {}
    products = Product.query.options(joinedload(Product.names))
    for product in products:
        for synonym in product.singular_names:
            synonyms[synonym] = list(product.singular_names)
    return synonyms


def recreate_product_synonym_index(index):
    settings = {"index": {"number_of_replicas": 0}}
    mapping = {"properties": {"synonyms": {"type": "keyword"}}}

    es = Elasticsearch("elasticsearch")
    es.indices.delete(index=index, ignore_unavailable=True)
    es.indices.create(index=index)
    es.indices.put_settings(index=index, body=settings)
    es.indices.put_mapping(index=index, body=mapping)


def populate_product_synonym_index(index, synonyms):
    es = Elasticsearch("elasticsearch")
    actions = []
    for product_name, product_synonyms in synonyms.items():
        actions.append(json.dumps({"index": {"_index": index, "_id": product_name}}))
        actions.append(json.dumps({"synonyms": synonyms}))
        if len(actions) % 100 == 0:
            es.bulk("\n".join(actions))
            actions.clear()
    es.indices.refresh(index=index)


@celery.task(queue="update_product_synonyms")
def update_product_synonyms():
    synonyms = get_product_synonyms()
    recreate_product_synonym_index("product_synonyms")
    populate_product_synonym_index("product_synonyms", synonyms)
