from elasticsearch import Elasticsearch
import json
import sys

es = Elasticsearch()

filename = sys.argv[1]
with open(filename, 'r') as f:
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
