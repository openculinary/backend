from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import sys

es = Elasticsearch('elasticsearch')
index = 'recipes'

try:
    es.indices.delete(index=index)
except NotFoundError:
    pass
except Exception:
    print('Failed to delete existing recipes')
    sys.exit(1)

mapping = {
    'properties': {
        'ingredients': {
            'type': 'nested',
            'properties': {
                'product': {
                    'properties': {
                        'product': {'type': 'keyword'},
                        'is_plural': {'type': 'boolean'},
                        'singular': {'type': 'keyword'},
                        'plural': {'type': 'keyword'},
                    }
                }
            }
        },
        'contents': {'type': 'keyword'}
    }
}
settings = {
    'index': {
        'number_of_replicas': 0,
        'refresh_interval': '300s',
    }
}

try:
    es.indices.create(index=index)
    es.indices.put_mapping(index=index, body=mapping)
    es.indices.put_settings(index=index, body=settings)
except Exception as e:
    print('Failed to create recipe index: {}'.format(e))
    sys.exit(1)
