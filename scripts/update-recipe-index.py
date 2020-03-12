import argparse
from elasticsearch import Elasticsearch
import sys

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
                },
                'equipment': {
                    'properties': {
                        'equipment': {'type': 'keyword'}
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
                        'category': {'type': 'keyword'},
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

parser = argparse.ArgumentParser(description='Configure recipes search index')
parser.add_argument('--hostname', required=True)
parser.add_argument('--index')
args = parser.parse_args()

es = Elasticsearch(args.hostname)
try:
    es.indices.put_mapping(index=args.index, body=mapping)
    es.indices.put_settings(index=args.index, body=settings)
except Exception as e:
    print('Failed to create recipe index: {}'.format(e))
    sys.exit(1)
