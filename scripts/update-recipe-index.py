import argparse
from elasticsearch import Elasticsearch
import sys

settings = {
    'index': {
        'number_of_replicas': 0,
        'refresh_interval': '300s',
    },
    'analysis': {
        'analyzer': {
            'autocomplete.analyze': {
                'tokenizer': 'autocomplete.tokenize',
                'filter': ['lowercase']
            },
            'autocomplete.search': {
                'tokenizer': 'lowercase',
                'filter': ['autocomplete.filter']
            }
        },
        'filter': {
            'autocomplete.filter': {
                'type': 'truncate',
                'length': 10
            }
        },
        'tokenizer': {
            'autocomplete.tokenize': {
                'type': 'edge_ngram',
                'min_ngram': 3,
                'max_ngram': 10,
                'token_chars': ['letter']
            }
        }
    }
}
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
                        'product_id': {'type': 'keyword'},
                        'product': {'type': 'text'},
                        'product.autocomplete': {
                            'type': 'text',
                            'analyzer': 'autocomplete.analyze',
                            'search_analyzer': 'autocomplete.search'
                        },
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

parser = argparse.ArgumentParser(description='Configure recipes search index')
parser.add_argument('--hostname', required=True)
parser.add_argument('--index')
args = parser.parse_args()

es = Elasticsearch(args.hostname)
try:
    es.indices.put_settings(index=args.index, body=settings)
    es.indices.put_mapping(index=args.index, body=mapping)
except Exception as e:
    print('Failed to create recipe index: {}'.format(e))
    sys.exit(1)
