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

        products = []
        after_key = True
        while after_key:

            # Execute product query
            results = self.es.search(index='recipes', body=query)
            results = results['aggregations']['products']

            # Collect product results
            products += [{
                'product': bucket['key']['product'],
                'recipe_count': bucket['doc_count'],
            } for bucket in results.get('buckets')]

            # Follow the resultset cursor
            after_key = results.get('after_key')
            query['aggregations']['products']['composite']['after'] = after_key

        return products
