from datetime import timedelta
from sqlalchemy import Column, DateTime, String

from reciperadar.models.base import Storable
from reciperadar.models.reminder_attendee import ReminderAttendee as Attendee
from reciperadar.services.calendar import get_calendar_api


class Reminder(Storable):
    __tablename__ = 'reminders'

    id = Column(String, primary_key=True)
    updated = Column(DateTime)
    summary = Column(String)
    description = Column(String)
    location = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    timezone = Column(String)

    @staticmethod
    def from_scheduled_recipe(recipe, start_time, timezone):
        return Reminder(
            summary=recipe['name'],
            description='\n'.join(recipe['ingredients']),
            location=recipe['url'],
            start_time=start_time,
            end_time=start_time + timedelta(minutes=recipe['time']),
            timezone=timezone
        )

    @staticmethod
    def from_webhook(data):
        reminder = Reminder(
            id=data['id'],
            updated=data['updated'],
            summary=data['summary'],
            start_time=data['start']['dateTime'],
            end_time=data['start']['dateTime'],
        )
        reminder.attendees = []
        for attendee in data['attendees']:
            attendee = Attendee.from_webhook(reminder.id, attendee)
            reminder.attendees.append(attendee)
        return reminder

    def _create_calendar_event(self, recipients):
        return {
            'summary': self.summary,
            'location': self.location,
            'description': self.description,
            'start': {
                'dateTime': self.start_time.isoformat(),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': self.end_time.isoformat(),
                'timeZone': self.timezone,
            },
            'attendees': [
                {'email': recipient} for recipient in recipients
            ],
            'guestsCanInviteOthers': True,
            'guestsCanModify': True,
        }

    def send(self, recipients):
        if not recipients:
            return

        calendar = get_calendar_api()
        calendar.events().insert(
            calendarId='primary',
            body=self._create_calendar_event(recipients),
            sendUpdates='all'
        ).execute()
