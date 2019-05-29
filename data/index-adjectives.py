from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()

with open('adjectives.json', 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index='adjectives', doc_type='adjective', body=doc)
        except:
            print('Failed to index adjective={}'.format(doc['name']))
