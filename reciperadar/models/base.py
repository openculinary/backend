from abc import ABC, abstractmethod, abstractproperty
from base58 import b58encode
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4


def decl_base(cls):
    return declarative_base(cls=cls)


@decl_base
class Storable(object):

    @staticmethod
    def generate_id(input_bytes=None):
        if not input_bytes:
            input_bytes = uuid4().bytes
        return b58encode(input_bytes).decode('utf-8')

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

    es = Elasticsearch('elasticsearch')

    @abstractmethod
    def from_doc(doc):
        pass

    @abstractproperty
    def noun(self):
        pass

    def get_by_id(self, id):
        try:
            doc = self.es.get(index=self.noun, id=id)
        except NotFoundError:
            return None
        return self.from_doc(doc['_source'])

    def index(self):
        if hasattr(self, 'indexed_at'):
            self.indexed_at = datetime.utcnow()
        self.es.index(index=self.noun, id=self.id, body=self.to_doc())
        return True
