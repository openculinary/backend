from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()

filename = sys.argv[1]
with open(filename, 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index='ingredients', doc_type='ingredient', body=doc)
        except:
            print('Failed to index ingredient={}'.format(doc))
