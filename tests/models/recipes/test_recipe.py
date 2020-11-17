from reciperadar.models.recipes import Recipe


def test_recipe_from_doc(db_session, raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit['_source'])

    # Commit recipe to the session; performs db object relationship resolution
    db_session.add(recipe)
    db_session.commit()

    assert recipe.author == 'example'

    assert recipe.directions[0].appliances[0].appliance == 'oven'
    assert recipe.directions[0].utensils[0].utensil == 'skewer'

    assert recipe.ingredients[0].product.product.singular == 'one'
    expected_contents = ['one', 'ancestor-of-one']
    actual_contents = recipe.ingredients[0].product.product.contents

    assert all([content in actual_contents for content in expected_contents])

    assert recipe.ingredients[0].nutrition.carbohydrates == 0
    assert recipe.ingredients[0].nutrition.fibre == 0.65
    assert recipe.ingredients[0].relative_density == 0.5

    assert recipe.aggregate_ingredient_nutrition == {
        'carbohydrates': 0,
        'energy': 0,
        'fat': 0.01,
        'fibre': 0.33,
        'protein': 0.03,
    }

    assert recipe.ingredients[0].product.product.is_vegan
    assert not recipe.ingredients[1].product.product.is_gluten_free

    assert not recipe.is_gluten_free
    assert not recipe.is_vegan
    assert recipe.is_vegetarian


def test_hidden_recipe(db_session, raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit['_source'])

    # Commit recipe to the session; performs db object relationship resolution
    db_session.add(recipe)
    db_session.commit()

    recipe.ingredients[0].product.product.singular = None

    doc = recipe.to_doc()

    assert doc.get('hidden') is True


def test_nutritional_filtering(db_session, raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit['_source'])

    # Commit recipe to the session; performs db object relationship resolution
    db_session.add(recipe)
    db_session.commit()

    assert recipe.ingredients[1].nutrition is None
    recipe.ingredients[1].magnitude = 500

    assert recipe.aggregate_ingredient_nutrition is None
