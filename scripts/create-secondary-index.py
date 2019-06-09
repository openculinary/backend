from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import isodate
import json
import sys

es = Elasticsearch()
index = 'recipes-secondary'

try:
    es.indices.delete(index=index)
except NotFoundError:
    pass
except:
    print('Failed to delete existing recipes')
    sys.exit(1)

mapping = {
    'properties': {
        'ingredients': {
            'type': 'nested',
            'properties': {
                'ingredient': {
                    'type': 'text',
                    'term_vector': 'with_positions_offsets'
                }
            }
        }
    }
}
try:
    es.indices.create(index=index)
    es.indices.put_mapping(index=index, doc_type='recipe', body=mapping)
except:
    print('Failed to create recipe mapping')
    sys.exit(1)
