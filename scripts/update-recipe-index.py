import argparse
from opensearchpy import OpenSearch
import sys

settings = {
    'index': {
        'number_of_replicas': 0,
        'refresh_interval': '300s',
    },
    'analysis': {
        'analyzer': {
            'autocomplete_analyze': {
                'tokenizer': 'autocomplete_tokenize',
                'filter': ['lowercase']
            },
            'autocomplete_search': {
                'tokenizer': 'standard',
                'filter': ['lowercase', 'autocomplete_filter']
            }
        },
        'filter': {
            'autocomplete_filter': {
                'type': 'truncate',
                'length': 10
            }
        },
        'tokenizer': {
            'autocomplete_tokenize': {
                'type': 'edge_ngram',
                'min_gram': 3,
                'max_gram': 10,
                'token_chars': ['letter']
            }
        }
    }
}
mapping = {
    'properties': {
        'ingredients': {
            'type': 'nested',
            'properties': {
                'product': {
                    'properties': {
                        'id': {'type': 'keyword'},
                        'category': {'type': 'keyword'},
                        'singular': {'type': 'keyword'},
                        'plural': {'type': 'keyword'},
                    }
                },
                'product_is_plural': {'type': 'boolean'},
                'product_name': {
                    'type': 'keyword',
                    'fields': {
                        'autocomplete': {
                            'type': 'text',
                            'analyzer': 'autocomplete_analyze',
                            'search_analyzer': 'autocomplete_search'
                        }
                    }
                }
            }
        },
        'contents': {'type': 'keyword'},
        'equipment_names': {'type': 'keyword'},
        'domain': {'type': 'keyword'}
    }
}

parser = argparse.ArgumentParser(description='Configure recipes search index')
parser.add_argument('--hostname', required=True)
parser.add_argument('--index')
args = parser.parse_args()

es = OpenSearch(args.hostname)
try:
    es.indices.close(index=args.index)
    es.indices.put_settings(index=args.index, body=settings)
    es.indices.put_mapping(index=args.index, body=mapping)
    es.indices.open(index=args.index)
except Exception as e:
    print('Failed to create recipe index: {}'.format(e))
    sys.exit(1)
