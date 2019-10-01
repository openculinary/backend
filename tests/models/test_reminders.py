import pytest

from datetime import datetime, timedelta

from reciperadar.models.reminder import Reminder


@pytest.fixture
def reminder_args():
    today_dt = datetime.combine(datetime.today(), datetime.min.time())
    future_meal_dt = today_dt + timedelta(weeks=1, hours=18)

    return {
        'start_time': future_meal_dt,
        'timezone': 'Europe/London',
        'collaboration_id': 'example-collaboration-id',
        'base_uri': 'example.com'
    }


def test_construct_reminder_from_shopping_list(reminder_args):
    Reminder.from_request(**reminder_args)
