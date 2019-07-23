from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()
index = 'ingredients'

try:
    es.indices.delete(index=index)
except NotFoundError:
    pass
except:
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

with open('data/ingredients/ingredients.json', 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index='ingredients', doc_type='ingredient', body=doc)
        except:
            print('Failed to index ingredient={}'.format(doc['name']))
