from reciperadar.models.base import Searchable


class Ingredient(Searchable):

    @property
    def noun(self):
        return 'recipes'

    def autosuggest(self, prefix):
        prefix = prefix.lower()
        query = {
          'aggregations': {
            # aggregate across all nested ingredient documents
            'ingredients': {
              'nested': {'path': 'ingredients'},
              'aggregations': {
                # filter to product names which match the user search
                'products': {
                  'filter': {
                    'bool': {
                      'should': [
                        {'match': {'ingredients.product.raw': prefix}},
                        {'prefix': {'ingredients.product.raw': prefix}}
                      ]
                    }
                  },
                  'aggregations': {
                    # retrieve the top products in singular pluralization
                    'product': {
                      'terms': {
                        'field': 'ingredients.product.singular',
                        'min_doc_count': 5,
                        'size': 10
                      },
                      'aggregations': {
                        # count products that were plural in the source recipe
                        'plurality': {
                          'filter': {
                            'match': {'ingredients.product.is_plural': True}
                          },
                          'aggregations': {
                            # return the plural word form in the results
                            'plural': {
                              'terms': {
                                'field': 'ingredients.product.plural',
                                'size': 1
                              }
                            }
                          }
                        }
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

        # iterate through the suggestions and determine whether to display
        # the singular or plural form of the word based on how frequently
        # each form is used in the overall recipe corpus
        suggestions = []
        for result in results:
            total_count = result['doc_count']
            plural_count = result['plurality']['doc_count']
            plural_docs = result['plurality']['plural']['buckets']
            plural_wins = plural_count > total_count - plural_count

            suggestion_doc = plural_docs[0] if plural_wins else result
            suggestions.append({'name': suggestion_doc['key']})

        suggestions.sort(key=lambda s: (
            s['name'] != prefix,  # exact matches first
            not s['name'].startswith(prefix),  # prefix matches next
            len(s['name'])),  # sort remaining matches by length
        )
        return suggestions
