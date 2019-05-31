from elasticsearch import Elasticsearch
from sqlalchemy.ext.declarative import declarative_base

Storable = declarative_base()


class Searchable(object):

    def __init__(self, noun):
        self.es = Elasticsearch()
        self.noun = noun

    @staticmethod
    def from_doc(doc):
        return doc['_source']

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

        return [
            self.from_doc(result)
            for result in results['hits']['hits']
        ]
