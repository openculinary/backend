from abc import ABC

from opensearchpy import OpenSearch


class QueryRepository(object):
    __metaclass__ = ABC

    es = OpenSearch("opensearch")
