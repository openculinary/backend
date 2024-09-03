from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import uuid4

from basest.core import encode
from opensearchpy import OpenSearch

from reciperadar import db


class Storable(db.Model):
    __abstract__ = True

    # Ref: the base58 reduced-ambiguity alphabet, sourced from the 'basest' test code
    ID_SYMBOL_TABLE = list("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")

    @staticmethod
    def generate_id(input_bytes=None):
        return str().join(
            encode(
                input_data=input_bytes or uuid4().bytes,
                input_base=256,
                input_symbol_table=list(range(256)),
                output_base=58,
                output_symbol_table=Storable.ID_SYMBOL_TABLE,
                output_padding="",
                input_ratio=16,
                output_ratio=22,
            )
        )

    @staticmethod
    @abstractmethod
    def from_doc(doc):
        pass

    def to_doc(self):
        # Index all database fields by default
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if not c.foreign_keys and getattr(self, c.name) is not None
        }


class Indexable:
    __metaclass__ = ABC

    es = OpenSearch("opensearch")

    def __init__(self):
        self.indexed_at = None

    @property
    @abstractmethod
    def noun(self):
        pass

    def index(self):
        if hasattr(self, "indexed_at"):
            self.indexed_at = datetime.now(tz=UTC)
        self.es.index(
            index=self.noun,
            id=self.id,
            body=self.to_doc(),
            timeout=300,
        )
        return True
