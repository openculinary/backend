from abc import ABC, abstractproperty
from elasticsearch import Elasticsearch
from sqlalchemy.ext.declarative import declarative_base


def decl_base(cls):
    return declarative_base(cls=cls)


@decl_base
class Storable(object):

    def to_json(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if not c.foreign_keys
        }


class Searchable(object):
    __metaclass__ = ABC

    def __init__(self):
        self.es = Elasticsearch()

    @abstractproperty
    def noun(self):
        pass

    @staticmethod
    def from_doc(doc):
        return doc['_source']

    def get_by_id(self, id):
        doc = self.es.get(index=self.noun, id=id)
        return self.from_doc(doc)

    def autosuggest(self, prefix):
        prefix = prefix.lower()
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
