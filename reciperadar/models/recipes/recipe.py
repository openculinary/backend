from pymmh3 import hash_bytes
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.direction import RecipeDirection
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.product import IngredientProduct


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = Column(String, primary_key=True)
    title = Column(String)
    src = Column(String)
    domain = Column(String)
    image_src = Column(String)
    time = Column(Integer)
    servings = Column(Integer)
    rating = Column(Float)
    ingredients = relationship(
        'RecipeIngredient',
        backref='recipe',
        passive_deletes='all'
    )
    directions = relationship(
        'RecipeDirection',
        backref='recipe',
        passive_deletes='all'
    )

    indexed_at = Column(DateTime)

    @property
    def noun(self):
        return 'recipes'

    @property
    def url(self):
        return f'/#action=view&id={self.id}'

    @property
    def products(self):
        products_by_id = {
            ingredient.product.singular: IngredientProduct(
                product=ingredient.product.product,
                singular=ingredient.product.singular,
            )
            for ingredient in self.ingredients
        }
        return list(products_by_id.values())

    @staticmethod
    def from_doc(doc):
        src_hash = hash_bytes(doc['src']).encode('utf-8')
        recipe_id = doc.get('id') or Recipe.generate_id(src_hash)
        return Recipe(
            id=recipe_id,
            title=doc['title'],
            src=doc['src'],
            domain=doc['domain'],
            image_src=doc.get('image_src'),
            ingredients=[
                RecipeIngredient.from_doc(ingredient)
                for ingredient in doc['ingredients']
                if ingredient['description'].strip()
            ],
            directions=[
                RecipeDirection.from_doc(direction)
                for direction in doc.get('directions') or []
                if direction['description'].strip()
            ],
            servings=doc['servings'],
            time=doc['time'],
            rating=doc['rating']
        )

    def to_dict(self, include=None):
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time,
            'ingredients': [
                ingredient.to_dict(include)
                for ingredient in self.ingredients
            ],
            'directions': [
                direction.to_dict()
                for direction in self.directions
            ],
            'servings': self.servings,
            'rating': self.rating,
            'src': self.src,
            'domain': self.domain,
            'url': self.url,
            'image_url': self.image_path,
        }

    @property
    def image_path(self):
        return f'images/recipes/{self.id}.png'

    @property
    def contents(self):
        contents = set()
        for product in self.products:
            contents |= set(product.contents)
        return list(contents)

    def to_doc(self):
        data = super().to_doc()
        data['directions'] = [
            direction.to_doc()
            for direction in self.directions
        ]
        data['ingredients'] = [
            ingredient.to_doc()
            for ingredient in self.ingredients
        ]
        data['contents'] = self.contents
        data['product_count'] = len(self.products)
        return data

    @staticmethod
    def _generate_include_clause(include):
        # sum the score of query ingredients found in the recipe
        return [{
            'constant_score': {
                'boost': 1,
                'filter': {'match': {'contents': inc}}
            }
        } for inc in include]

    @staticmethod
    def _generate_exclude_clause(exclude):
        # match any ingredients in the exclude list
        return [{'match': {'contents': exc}} for exc in exclude]

    @staticmethod
    def _generate_equipment_clause(equipment):
        return [
            {'match': {'directions.equipment.equipment': item}}
            for item in equipment
        ]

    @staticmethod
    def _generate_sort_params(include, sort):
        # don't score relevance searches if no query ingredients are provided
        if sort == 'relevance' and not include:
            return {'script': '0', 'order': 'desc'}

        preamble = '''
            def inv_score = 1 / (_score + 1);
            def product_count = doc.product_count.value;
            def missing_count = product_count - _score;

            def missing_ratio = missing_count / product_count;
            def normalized_rating = doc.rating.value / 10;
        '''
        sort_configs = {
            # rank: number of ingredient matches
            # tiebreak: recipe rating
            'relevance': {
                'script': f'{preamble} _score + normalized_rating',
                'order': 'desc'
            },

            # rank: number of missing ingredients
            # tiebreak: recipe rating
            'ingredients': {
                'script': f'{preamble} missing_count + normalized_rating',
                'order': 'asc'
            },

            # rank: preparation time
            # tiebreak: percentage of missing ingredients
            'duration': {
                'script': f'{preamble} doc.time.value + missing_ratio',
                'order': 'asc'
            },
        }
        return sort_configs[sort]

    def _render_query(self, include, exclude, equipment, sort, match_all=True):
        include_clause = self._generate_include_clause(include)
        exclude_clause = self._generate_exclude_clause(exclude)
        equipment_clause = self._generate_equipment_clause(equipment)
        sort_params = self._generate_sort_params(include, sort)

        filter_clause = [
            {'range': {'time': {'gte': 5}}},
            {'range': {'product_count': {'gt': 0}}},
        ]
        if equipment_clause:
            filter_clause += equipment_clause

        return {
            'function_score': {
                'boost_mode': 'replace',
                'query': {
                    'bool': {
                        'must' if match_all else 'should': include_clause,
                        'must_not': exclude_clause,
                        'filter': filter_clause,
                        'minimum_should_match': None if match_all else 1
                    }
                },
                'script_score': {'script': {'source': sort_params['script']}}
            }
        }, [{'_score': sort_params['order']}]

    def _refined_queries(self, include, exclude, equipment, sort_order):
        query, sort = self._render_query(
            include=include,
            exclude=exclude,
            equipment=equipment,
            sort=sort_order
        )
        yield query, sort, None

        item_count = len(include)
        if item_count > 3:
            for _ in range(item_count):
                removed = include.pop(0)
                query, sort = self._render_query(
                    include=include,
                    exclude=exclude,
                    equipment=equipment,
                    sort=sort_order
                )
                yield query, sort, f'removed:{removed}'
                include.append(removed)

        if item_count > 1:
            query, sort = self._render_query(
                include=include,
                exclude=exclude,
                equipment=equipment,
                sort=sort_order,
                match_all=False
            )
            yield query, sort, 'match_any'

    def search(self, include, exclude, equipment, offset, limit, sort_order):
        offset = max(0, offset)
        limit = max(1, limit)
        limit = min(25, limit)
        sort_order = sort_order or 'relevance'

        queries = self._refined_queries(
            include=include,
            exclude=exclude,
            equipment=equipment,
            sort_order=sort_order
        )
        for query, sort, refinement in queries:
            results = self.es.search(
                index=self.noun,
                body={
                    'from': offset,
                    'size': limit,
                    'query': query,
                    'sort': sort,
                }
            )
            if results['hits']['total']['value']:
                break

        recipes = []
        for result in results['hits']['hits']:
            recipe = Recipe.from_doc(result['_source'])
            recipes.append(recipe.to_dict(include))

        return {
            'authority': 'api',
            'total': min(results['hits']['total']['value'], 25 * limit),
            'results': recipes,
            'refinements': [refinement] if refinement else []
        }
