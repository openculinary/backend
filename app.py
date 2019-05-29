from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
app = Flask(__name__)


def autosuggest(noun, prefix):
    es = Elasticsearch()
    results = es.search(
        index=noun,
        body={
            'query': {
                'bool': {
                    'filter': {'wildcard': {'name': '{}*'.format(prefix)}}
                }
            }
        }
    )
    results = results['hits']['hits']
    results = [result.pop('_source').pop('name') for result in results]
    results.sort(key=lambda name: len(name))
    return results


@app.route('/api/adjectives')
def adjectives():
    prefix = request.args.get('pre')
    results = autosuggest('adjectives', prefix)
    return jsonify(results)


@app.route('/api/courses')
def courses():
    prefix = request.args.get('pre')
    results = autosuggest('courses', prefix)
    return jsonify(results)


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    results = autosuggest('ingredients', prefix)
    return jsonify(results)


def format_recipe(doc):
    source = doc.pop('_source')

    title = source.pop('name')
    image = source.pop('image')
    time = source.pop('cookTime', None)
    url = source.pop('url')

    matches = []
    highlights = doc.get('highlight', {}).get('ingredients', [])
    for highlight in highlights:
        bs = BeautifulSoup(highlight)
        matches += [em.text.lower() for em in bs.findAll('em')]
    matches = list(set(matches))

    return {
        'title': title,
        'image': image,
        'time': time,
        'url': url,
        'matches': matches
    }


@app.route('/api/recipes')
def recipes():
    include = request.args.getlist('include[]')
    include_match = [{'match_phrase': {'ingredients': inc}} for inc in include]

    exclude = request.args.getlist('exclude[]')
    exclude_match = [{'match_phrase': {'ingredients': exc}} for exc in exclude]

    es = Elasticsearch()
    results = es.search(
        index='recipes',
        body={
            'query': {
                'bool': {
                    'must': include_match,
                    'must_not': exclude_match,
                    'filter': {'wildcard': {'image': '*'}}
                }
            },
            'highlight': {
                'type': 'fvh',
                'fields': {
                    'ingredients': {}
                }
            }
        }
    )
    results = results['hits']['hits']
    results = [format_recipe(result) for result in results]
    return jsonify(results)
