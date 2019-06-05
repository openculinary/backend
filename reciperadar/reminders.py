from datetime import timedelta
from google.oauth2.service_account import Credentials
from googleapiclient import discovery


class MealReminder(object):

    def __init__(self, recipe, recipients, start_time, timezone):
        self.title = recipe['name']
        self.duration = timedelta(minutes=recipe['time'])
        self.ingredients = '\n'.join(recipe['ingredients'])
        self.url = recipe['url']
        self.start_time = start_time
        self.end_time = start_time + timedelta(minutes=recipe['time'])
        self.timezone = timezone
        self.recipients = recipients

    def _get_calendar_api(self):
        credentials = Credentials.from_service_account_file(
            filename='../credentials/calendar_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events']
        ).with_subject('calendar@reciperadar.com')
        return discovery.build('calendar', 'v3', credentials=credentials)

    def _create_calendar_event(self):
        return {
            'summary': self.title,
            'location': self.url,
            'description': self.ingredients,
            'start': {
                'dateTime': self.start_time.isoformat(),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': self.end_time.isoformat(),
                'timeZone': self.timezone,
            },
            'attendees': [
                {'email': recipient} for recipient in self.recipients
            ]
        }

    def send(self):
        if not self.recipients:
            return

        event = self._create_calendar_event()
        calendar = self._get_calendar_api()
        calendar.events().insert(
            calendarId='calendar@reciperadar.com',
            body=event,
            sendNotifications=True
        ).execute()
