from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()
try:
    query = {'query': {'match_all': {}}}
    es.delete_by_query(index='ingredients', body=query)
except:
    print('Failed to delete existing ingredients')
    sys.exit(1)

with open('ingredients.json', 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index='ingredients', doc_type='ingredient', body=doc)
        except:
            print('Failed to index ingredient={}'.format(doc['name']))
