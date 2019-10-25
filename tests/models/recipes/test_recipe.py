from reciperadar.models.recipes import Recipe


def test_recipe_from_doc(raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit['_source'])

    assert recipe.directions[0].appliances[0].appliance == 'oven'
    assert recipe.directions[0].utensils[0].utensil == 'skewer'


def test_image_ext(raw_recipe_hit):
    r = Recipe().from_doc(raw_recipe_hit['_source'])
    assert r.image_ext == 'png'
