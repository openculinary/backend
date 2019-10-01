from datetime import timedelta
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from reciperadar.models.base import Storable
from reciperadar.services.calendar import get_calendar_api


class ReminderAttendee(Storable):
    __tablename__ = 'reminder_attendees'

    fk = ForeignKey('reminders.id', ondelete='cascade')
    reminder_id = Column(String, fk, primary_key=True)
    email = Column(String, primary_key=True)

    @staticmethod
    def from_webhook(data):
        return ReminderAttendee(
            email=data['email']
        )


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
    attendees = relationship(
        'ReminderAttendee',
        backref='reminder',
        passive_deletes='all'
    )

    @staticmethod
    def from_request(base_uri, collaboration_id, start_time, timezone):
        location = f'{base_uri}#action=join&collaborationId={collaboration_id}'

        return Reminder(
            summary='Your shopping list',
            location=location,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            timezone=timezone
        )

    @staticmethod
    def from_webhook(data):
        return Reminder(
            id=data['id'],
            updated=data['updated'],
            summary=data['summary'],
            start_time=data['start']['dateTime'],
            end_time=data['start']['dateTime'],
            attendees=[
                ReminderAttendee.from_webhook(attendee)
                for attendee in data['attendees']
            ]
        )

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
