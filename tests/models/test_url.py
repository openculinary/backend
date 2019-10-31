from reciperadar.models.url import RecipeURL


def test_url_domain():
    url = RecipeURL(url='https://recipe.subdomain.example.com/recipe/123')

    assert url.domain == 'example.com'
