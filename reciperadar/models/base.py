from abc import ABC, abstractproperty
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from sqlalchemy.ext.declarative import declarative_base


def decl_base(cls):
    return declarative_base(cls=cls)


@decl_base
class Storable(object):

    def to_dict(self):
        # Return the doc representation by default
        return self.to_doc()

    def to_doc(self):
        # Index all database fields by default
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

    def get_by_id(self, id):
        try:
            doc = self.es.get(index=self.noun, id=id)
        except NotFoundError:
            return None
        return self.from_doc(doc)

    def index(self):
        doc = self.to_doc()
        doc_type = self.noun[:-1]
        self.es.index(index=self.noun, doc_type=doc_type, id=self.id, body=doc)
