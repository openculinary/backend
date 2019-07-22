import isodate
import json
import re
import requests


verbs = []
with open('verbs.txt', 'r') as f:
    verbs = f.readlines()
    verbs = set([verb.strip() for verb in verbs])


def parse_ingredients(text):
    results = []
    for token in text.split('\n'):
        verb = None
        if token.startswith(','):
            for verb in verbs:
                verb_phrase = ', for {}'.format(verb)
                if verb_phrase in token:
                    token = token.replace(verb_phrase, '')
                    break
        results.append({'ingredient': token, 'verb': verb})
    return results


def parse_doc(doc):
    title = doc.pop('name')
    url = doc.pop('url')
    ingredients = doc.pop('ingredients')
    image = doc.pop('image', None)
    servings = doc.pop('recipeYield', 1)
    time = doc.pop('cookTime', None)

    if time:
        time = isodate.parse_duration(time)
        time = int(time.total_seconds() / 60)

    if image and not image.startswith('http'):
        domain = '/'.join(url.split('/')[0:3])
        image = domain + image

    servings = str(servings)
    m = re.search('^(\d+)', servings)
    if m:
        servings = m.group(0)
    try:
        servings = int(servings)
    except ValueError:
        servings = 1

    ingredients = parse_ingredients(ingredients)

    return {
        'title': title,
        'url': url,
        'ingredients': ingredients,
        'image': image,
        'servings': servings,
        'time': time,
    }


with open('recipes.json', 'r') as f:
    fragments = []
    for line in f:
        fragments.append(line)
        if line.startswith('}'):
            doc = json.loads(''.join(fragments))
            doc = parse_doc(doc)
            if not doc:
                fragments = []
                continue

            ingest_uri = 'http://localhost:8080/api/recipes/ingest'
            try:
                requests.post(
                    url=ingest_uri,
                    json=doc
                )
                print('* Ingested {}'.format(doc['title']))
            except Exception:
                pass
            fragments = []
