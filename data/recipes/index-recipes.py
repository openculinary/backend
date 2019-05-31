from elasticsearch import Elasticsearch
import isodate
import json
import sys

es = Elasticsearch()
try:
    es.indices.delete(index='recipes')
except:
    print('Failed to delete existing recipes')
    sys.exit(1)


mapping = {
    'properties': {
        'ingredients': {
            'type': 'text',
            'term_vector': 'with_positions_offsets'
        }
    }
}
try:
    es.indices.create(index='recipes')
    es.indices.put_mapping(index='recipes', doc_type='recipe', body=mapping)
except:
    print('Failed to create recipe mapping')
    sys.exit(1)


def parse_doc(doc):
    name = doc.pop('name')
    image = doc.pop('image', None)
    time = doc.pop('cookTime', None)
    url = doc.pop('url')

    if time:
        time = isodate.parse_duration(time)
        time = int(time.total_seconds() / 60)

    return doc['_id']['$oid'], {
        'name': name,
        'image': image,
        'time': time,
        'url': url,
    }


with open('recipes.json', 'r') as f:
    fragments = []
    for line in f:
        fragments.append(line)
        if line.startswith('}'):
            doc = json.loads(''.join(fragments))
            id, doc = parse_doc(doc)
            try:
                es.index(index='recipes', doc_type='recipe', id=id, body=doc)
            except:
                print('Failed to index doc-id={}'.format(id))
            fragments = []
