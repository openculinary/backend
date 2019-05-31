from elasticsearch import Elasticsearch


class Searchable(object):

    def __init__(self, noun):
        self.es = Elasticsearch()
        self.noun = noun

    def autosuggest(self, prefix):
        results = self.es.search(
            index=self.noun,
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
