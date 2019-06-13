from abc import ABC, abstractproperty
from elasticsearch import Elasticsearch
from sqlalchemy.ext.declarative import declarative_base


def decl_base(cls):
    return declarative_base(cls=cls)


@decl_base
class Storable(object):

    def to_dict(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if not c.foreign_keys
        }


class Searchable(object):
    __metaclass__ = ABC

    @property
    def es(self):
        if not hasattr(self, '_es'):
            self._es = Elasticsearch()
        return self._es

    @abstractproperty
    def noun(self):
        pass

    @staticmethod
    def from_doc(doc):
        return doc['_source']

    def get_by_id(self, id, secondary=False):
        index = self.noun
        if secondary:
            index += '-secondary'
        doc = self.es.get(index=index, id=id)
        return self.from_doc(doc)

    def index(self, secondary=True):
        doc = self.to_dict()
        index = self.noun
        if secondary:
            index += '-secondary'
        doc_type = self.noun[:-1]
        self.es.index(index=index, doc_type=doc_type, id=self.id, body=doc)

    def autosuggest(self, prefix, secondary=False):
        index = self.noun
        if secondary:
            index += '-secondary'
        prefix = prefix.lower()
        results = self.es.search(
            index=index,
            body={
                'query': {
                    'bool': {
                        'should': [
                            {'match': {'name': prefix}},
                            {'prefix': {'name': {'value': prefix}}},
                        ]
                    }
                },
                'size': 25
            }
        )
        results = [
            self.from_doc(result)
            for result in results['hits']['hits']
        ]
        results.sort(key=lambda r: (
            r['name'] != prefix,  # exact matches first
            not r['name'].startswith(prefix),  # prefix matches next
            len(r['name'])),  # sort remaining matches by length
        )
        return results[:10]
