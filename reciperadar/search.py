from elasticsearch import Elasticsearch


class SearchEngine(object):

    def __init__(self):
        self.es = Elasticsearch()

    def autosuggest(self, noun, prefix):
        results = self.es.search(
            index=noun,
            body={
                'query': {
                    'bool': {
                        'should': [
                            {'match': {'name': prefix}},
                            {'wildcard': {'name': '{}*'.format(prefix)}},
                        ]
                    }
                }
            }
        )
        results = results['hits']['hits']
        results = [result.pop('_source').pop('name') for result in results]
        return results

    def recipe_search(self, include, exclude):
        include = [{'match_phrase': {'ingredients': inc}} for inc in include]
        exclude = [{'match_phrase': {'ingredients': exc}} for exc in exclude]

        results = self.es.search(
            index='recipes',
            body={
                'query': {
                    'bool': {
                        'must': include,
                        'must_not': exclude,
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
        return results['hits']['hits']
