import isodate
import json
import requests


def parse_doc(doc):
    title = doc.pop('name')
    url = doc.pop('url')
    ingredients = doc.pop('ingredients')
    image = doc.pop('image', None)
    time = doc.pop('cookTime', None)

    if time:
        time = isodate.parse_duration(time)
        time = int(time.total_seconds() / 60)

    if image and not image.startswith('http'):
        domain = '/'.join(url.split('/')[0:3])
        image = domain + image

    return {
        'title': title,
        'url': url,
        'ingredients': ingredients.split('\n'),
        'image': image,
        'time': time,
    }


with open('recipes.json', 'r') as f:
    fragments = []
    for line in f:
        fragments.append(line)
        if line.startswith('}'):
            doc = json.loads(''.join(fragments))
            doc = parse_doc(doc)
            ingest_uri = 'http://localhost:8080/api/recipes/ingest'
            try:
                requests.post(
                    url=ingest_uri,
                    json=doc
                )
            except Exception:
                pass
            fragments = []
