from abc import ABC

from elasticsearch import Elasticsearch


class QueryRepository(object):
    __metaclass__ = ABC

    es = Elasticsearch('elasticsearch')
