from reciperadar.models.recipe import Recipe


def test_recipe_from_doc(raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit)
    expected_keys = set(['name', 'ingredients', 'time', 'image', 'url'])

    assert expected_keys.issubset(recipe.keys())
