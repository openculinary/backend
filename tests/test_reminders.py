import pytest

from datetime import datetime, timedelta

from reciperadar.models.recipe import Recipe
from reciperadar.models.reminder import Reminder


@pytest.fixture
def future_meal_args(raw_recipe_hit):
    recipe = Recipe.from_doc(raw_recipe_hit)
    today_dt = datetime.combine(datetime.today(), datetime.min.time())
    future_meal_dt = today_dt + timedelta(weeks=1, hours=18)

    return {
        'recipe': recipe,
        'start_time': future_meal_dt,
        'timezone': 'Europe/London',
    }


def test_construct_reminder_from_recipe(future_meal_args):
    Reminder.from_scheduled_recipe(**future_meal_args)
