import pytest

from datetime import datetime, timedelta

from reciperadar.models.reminder import Reminder


@pytest.fixture
def future_shopping_list_args(raw_recipe_hit):
    today_dt = datetime.combine(datetime.today(), datetime.min.time())
    future_meal_dt = today_dt + timedelta(weeks=1, hours=18)

    return {
        'shopping_list': {
            'products': {'example': {
                'raw': 'example',
                'singular': 'example',
                'plural': 'examples',
            }}
        },
        'start_time': future_meal_dt,
        'timezone': 'Europe/London',
        'base_uri': 'example.com'
    }


def test_construct_reminder_from_shopping_list(future_shopping_list_args):
    Reminder.from_shopping_list(**future_shopping_list_args)
