from reciperadar.models.base import Searchable


class RecipeEquipment(Searchable):

    def autosuggest(self, prefix):
        prefix = prefix.lower()
        query = {
          'aggregations': {
            'equipment': {
              'filter': {
                'bool': {
                  'should': [
                    {'match': {'directions.equipment.equipment': prefix}},
                    {'prefix': {'directions.equipment.equipment': prefix}}
                  ]
                }
              },
              'aggregations': {
                'equipment': {
                  'terms': {
                    'field': 'directions.equipment.equipment',
                    'include': f'{prefix}.*',
                    'min_doc_count': 1,
                    'size': 10
                  }
                }
              }
            }
          }
        }
        results = self.es.search(index=self.noun, body=query)['aggregations']
        results = results['equipment']['equipment']['buckets']

        results.sort(key=lambda s: (
            s['key'] != prefix,  # exact matches first
            not s['key'].startswith(prefix),  # prefix matches next
            len(s['key'])),  # sort remaining matches by length
        )
        return [
            {'equipment': result['key']}
            for result in results
        ]
