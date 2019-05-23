from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/ingredients')
def ingredients():
    es = Elasticsearch()
    pre = request.args.get('pre')

    results = es.search(
        index='ingredients',
        body={
            'query': {
                'bool': {
                    'filter': {'wildcard': {'name': '{}*'.format(pre)}}
                }
            }
        }
    )
    results = results['hits']['hits']
    results = [result.pop('_source').pop('name') for result in results]
    results.sort(key=lambda name: len(name))
    return jsonify(results)

@app.route('/recipes')
def recipes():
    es = Elasticsearch()
    include = request.args.getlist('include[]')
    include = [{'match': {'ingredients': inc}} for inc in include]

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
