from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()
try:
    query = {'query': {'match_all': {}}}
    es.delete_by_query(index='adjectives', body=query)
except:
    print('Failed to delete existing adjectives')
    sys.exit(1)

with open('adjectives.json', 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index='adjectives', doc_type='adjective', body=doc)
        except:
            print('Failed to index adjective={}'.format(doc['name']))
