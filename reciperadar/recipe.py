from reciperadar.base import Searchable


class Recipe(Searchable):

    def __init__(self):
        super().__init__(noun='recipes')

    def search(self, include, exclude):
        include = [{'match_phrase': {'ingredients': inc}} for inc in include]
        exclude = [{'match_phrase': {'ingredients': exc}} for exc in exclude]

        results = self.es.search(
            index='recipes',
            body={
                'query': {
                    'bool': {
                        'must': include,
                        'must_not': exclude,
                        'filter': {'wildcard': {'image': '*'}}
                    }
                },
                'highlight': {
                    'type': 'fvh',
                    'fields': {
                        'ingredients': {}
                    }
                }
            }
        )
        return results['hits']['hits']
