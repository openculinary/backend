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


@app.route('/api/recipes')
def recipes():
    include = request.args.getlist('include[]')
    include = [{'match': {'ingredients': inc}} for inc in include]

    es = Elasticsearch()
    results = es.search(
        index='recipes',
        body={
            'query': {
                'bool': {
                    'must': include,
                    'filter': {'wildcard': {'image': '*'}}
                }
            }
        }
    )
    results = results['hits']['hits']
    results = [result.pop('_source') for result in results]
    return jsonify(results)
