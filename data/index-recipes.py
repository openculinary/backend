from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()
try:
    query = {'query': {'match_all': {}}}
    es.delete_by_query(index='recipes', body=query)
except:
    print('Failed to delete existing recipes')
    sys.exit(1)

with open('recipes.json', 'r') as f:
    fragments = []
    for line in f:
        fragments.append(line)
        if line.startswith('}'):
            doc = json.loads(''.join(fragments))
            id = doc.pop('_id').pop('$oid')
            try:
                es.index(index='recipes', doc_type='recipe', id=id, body=doc)
            except:
                print('Failed to index doc-id={}'.format(id))
            fragments = []
