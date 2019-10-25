from elasticsearch import Elasticsearch
import sys

es = Elasticsearch('elasticsearch')
index = 'recipes'

mapping = {
    'properties': {
        'directions': {
            'properties': {
                'appliances': {
                    'properties': {
                        'appliance': {'type': 'keyword'}
                    }
                },
                'utensils': {
                    'properties': {
                        'utensil': {'type': 'keyword'}
                    }
                }
            }
        },
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
    es.indices.put_mapping(index=index, body=mapping)
    es.indices.put_settings(index=index, body=settings)
except Exception as e:
    print('Failed to create recipe index: {}'.format(e))
    sys.exit(1)
