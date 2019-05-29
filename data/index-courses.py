from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()

with open('courses.json', 'r') as f:
    for line in f:
        doc = json.loads(line)
        try:
            es.index(index='courses', doc_type='course', body=doc)
        except:
            print('Failed to index course={}'.format(doc['name']))
