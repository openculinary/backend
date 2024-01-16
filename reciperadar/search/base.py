from abc import ABC

from opensearchpy import OpenSearch


class QueryRepository:
    __metaclass__ = ABC

    es = OpenSearch("opensearch")
