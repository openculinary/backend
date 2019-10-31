from reciperadar.search.base import QueryRepository


class ProductSearch(QueryRepository):

    def products(self):
        query = {
            'aggregations': {
                'products': {
                    'composite': {
                        'size': 250,
                        'sources': [
                            {'product': {'terms': {'field': 'contents'}}}
                        ]
                    }
                }
            }
        }

        after_key = True
        while after_key:

            # Execute product query
            results = self.es.search(index='recipes', body=query)
            results = results['aggregations']['products']

            # Yield product results
            for bucket in results.get('buckets'):
                yield {
                    'product': bucket['key']['product'],
                    'recipe_count': bucket['doc_count'],
                }

            # Follow the resultset cursor
            after_key = results.get('after_key')
            query['aggregations']['products']['composite']['after'] = after_key
