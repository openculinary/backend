from reciperadar.models.base import Searchable


class Ingredient(Searchable):

    @property
    def noun(self):
        return 'recipes'

    def autosuggest(self, prefix):
        prefix = prefix.lower()
        query = {
          'aggregations': {
            'ingredients': {
              'nested': {'path': 'ingredients'},
              'aggregations': {
                'products': {
                  'filter': {
                    'bool': {
                      'should': [
                        {'match': {'ingredients.product': prefix}},
                        {'prefix': {'ingredients.product': prefix}}
                      ]
                    }
                  },
                  'aggregations': {
                    'product': {
                      'terms': {
                        'field': 'ingredients.product',
                        'min_doc_count': 5,
                        'size': 10
                      }
                    }
                  }
                }
              }
            }
          }
        }
        results = self.es.search(index=self.noun, body=query)['aggregations']
        results = results['ingredients']['products']['product']['buckets']
        results = [{'name': result['key']} for result in results]
        results.sort(key=lambda r: (
            r['name'] != prefix,  # exact matches first
            not r['name'].startswith(prefix),  # prefix matches next
            len(r['name'])),  # sort remaining matches by length
        )
        return results
