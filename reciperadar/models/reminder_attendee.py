from sqlalchemy import Column, ForeignKey, String

from reciperadar.models.base import Storable


class ReminderAttendee(Storable):
    __tablename__ = 'reminder_attendees'

    reminder_id = Column(String, ForeignKey('reminders.id'), primary_key=True)
    attendee_email = Column(String, primary_key=True)

    @staticmethod
    def from_webhook(reminder_id, data):
        return ReminderAttendee(
            reminder_id=reminder_id,
            attendee_email=data['email']
        )
