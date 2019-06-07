from bs4 import BeautifulSoup

from reciperadar.models.base import Searchable


class Recipe(Searchable):

    @property
    def noun(self):
        return 'recipes'

    @staticmethod
    def from_doc(doc):
        matches = []
        highlights = doc.get('highlight', {}).get('ingredients', [])
        for highlight in highlights:
            bs = BeautifulSoup(highlight)
            matches += [em.text.lower() for em in bs.findAll('em')]
        matches = list(set(matches))

        source = doc.pop('_source')
        return {
            'id': doc['_id'],
            'image': source['image'],
            'ingredients': source['ingredients'],
            'matches': matches,
            'name': source['name'],
            'time': source['time'],
            'url': source['url'],
        }

    def search(self, include, exclude):
        include = [{'match_phrase': {'ingredients': inc}} for inc in include]
        exclude = [{'match_phrase': {'ingredients': exc}} for exc in exclude]
        exclude += [{'match': {'name': 'dog'}}]
        time_filter = [{'range': {'time': {'gt': 5}}}]

        results = self.es.search(
            index='recipes',
            body={
                'query': {
                    'bool': {
                        'must': include + time_filter,
                        'must_not': exclude,
                        'filter': {'wildcard': {'image': '*'}},
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

        return [
            self.from_doc(result)
            for result in results['hits']['hits']
        ]
