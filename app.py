from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/recipes')
def recipes():
    es = Elasticsearch()
    q = request.args.get('q')

    results = es.search(
        index='recipes',
        body={
            'query': {
                'bool': {
                    'must': [{'match': {'ingredients': q}}],
                    'filter': {'wildcard': {'image': '*'}}
                }
            }
        }
    )
    results = results['hits']['hits']
    results = [result.pop('_source') for result in results]
    return jsonify(results)
