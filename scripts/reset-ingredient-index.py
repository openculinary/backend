from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import json
import sys

es = Elasticsearch()
index = 'ingredients'

try:
    es.indices.delete(index=index)
except NotFoundError:
    pass
except Exception:
    print('Failed to delete existing ingredients')
    sys.exit(1)

settings = {
    'index': {
        'number_of_replicas': 0,
        'refresh_interval': '300s',
    }
}

try:
    es.indices.create(index=index)
    es.indices.put_settings(index=index, body=settings)
except Exception as e:
    print('Failed to create ingredient index: {}'.format(e))
    sys.exit(1)

with open('scripts/data/ingredients.json', 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index=index, body=doc)
        except Exception:
            print('Failed to index ingredient={}'.format(doc['name']))

try:
    es.indices.refresh(index=index)
except Exception:
    print('Failed to refresh ingredients index')
