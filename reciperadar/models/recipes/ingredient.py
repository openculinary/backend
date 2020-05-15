from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.product import IngredientProduct


class RecipeIngredient(Storable, Searchable):
    __tablename__ = 'recipe_ingredients'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    index = Column(Integer)
    description = Column(String)
    markup = Column(String)
    product = relationship(
        'IngredientProduct',
        backref='recipe_ingredient',
        uselist=False,
        passive_deletes='all'
    )

    quantity = Column(Float)
    quantity_parser = Column(String)
    units = Column(String)
    units_parser = Column(String)
    verb = Column(String)

    @staticmethod
    def from_doc(doc):
        ingredient_id = doc.get('id') or RecipeIngredient.generate_id()
        return RecipeIngredient(
            id=ingredient_id,
            index=doc.get('index'),  # TODO
            description=doc['description'].strip(),
            markup=doc.get('markup'),
            product=IngredientProduct.from_doc(doc['product']),
            quantity=doc.get('quantity'),
            quantity_parser=doc.get('quantity_parser'),
            units=doc.get('units'),
            units_parser=doc.get('units_parser'),
            verb=doc.get('verb')
        )

    def to_dict(self, include=None):
        return {
            'markup': self.markup,
            'product': self.product.to_dict(include),
        }

    def to_doc(self):
        data = super().to_doc()
        data['product'] = self.product.to_doc()
        return data

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
                        {'match': {'ingredients.product.product': prefix}},
                        {'prefix': {'ingredients.product.product': prefix}}
                      ]
                    }
                  },
                  'aggregations': {
                    # retrieve the top products in singular pluralization
                    'product_id': {
                      'terms': {
                        'field': 'ingredients.product.product_id',
                        'min_doc_count': 5,
                        'size': 10
                      },
                      'aggregations': {
                        # count products that were plural in the source recipe
                        'plurality': {
                          'filter': {
                            'match': {'ingredients.product.is_plural': True}
                          }
                        },
                        # retrieve a category for each ingredient
                        'category': {
                          'terms': {
                            'field': 'ingredients.product.category',
                            'size': 1
                          }
                        },
                        'singular': {
                          'terms': {
                            'field': 'ingredients.product.singular',
                            'size': 1
                          }
                        },
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
        results = self.es.search(index=self.noun, body=query)['aggregations']
        results = results['ingredients']['products']['product_id']['buckets']

        # iterate through the suggestions and determine whether to display
        # the singular or plural form of the word based on how frequently
        # each form is used in the overall recipe corpus
        suggestions = []
        for result in results:
            total_count = result['doc_count']
            plural_count = result['plurality']['doc_count']
            plural_wins = plural_count > total_count - plural_count

            product_id = result['key']
            category = (result['category']['buckets'] or [{}])[0].get('key')
            singular = (result['singular']['buckets'] or [{}])[0].get('key')
            plural = (result['plural']['buckets'] or [{}])[0].get('key')

            suggestions.append(IngredientProduct(
                product_id=product_id,
                product=plural if plural_wins else singular,
                category=category,
                singular=singular,
                plural=plural,
            ))

        suggestions.sort(key=lambda s: (
            s.product != prefix,  # exact matches first
            not s.product.startswith(prefix),  # prefix matches next
            len(s.product)),  # sort remaining matches by length
        )
        return [{
            'product_id': suggestion.product_id,
            'product': suggestion.product,
            'category': suggestion.category,
            'singular': suggestion.singular,
            'plural': suggestion.plural,
        } for suggestion in suggestions]
