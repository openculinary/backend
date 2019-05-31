from flask_mail import Message
from icalendar import Calendar, Event, vCalAddress, vText
from uuid import uuid4

from reciperadar.app import mail


class MealReminder(object):

    def __init__(self, title, start_time, duration):
        self.title = title
        self.start_time = start_time
        self.duration = duration

    def create_organizer(self):
        organizer = vCalAddress('MAILTO:calendar@reciperadar.com')
        organizer.params['cn'] = vText('Recipe Radar')
        organizer.params['role'] = vText('CHAIR')
        return organizer

    def create_attendee(self, recipient):
        attendee = vCalAddress('MAILTO:{}'.format(recipient))
        attendee.params['role'] = vText('REQ-PARTICIPANT')
        return attendee

    def create_event(self, organizer):
        event = Event()
        event.add('summary', 'Test Meeting')
        event.add('dtstart', self.start_time)
        event.add('dtend', self.start_time + self.duration)
        event.add('uid', vText(uuid4()))
        event.add('organizer', organizer)
        return event

    def create_calendar(self, event):
        calendar = Calendar()
        calendar.add('prodid', '-//Recipe Radar//staging.reciperadar.com//')
        calendar.add('version', '2.0')
        calendar.add('method', 'REQUEST')
        calendar.add_component(event)
        return calendar

    def generate_ical(self, recipients):
        organizer = self.create_organizer()
        event = self.create_event(organizer)
        for recipient in recipients:
            attendee = self.create_attendee(recipient)
            event.add('attendee', attendee)
        calendar = self.create_calendar(event)
        return calendar.to_ical()

    def send(self, recipients):
        msg = Message(
            subject=self.title,
            sender='calendar@reciperadar.com',
            recipients=recipients
        )
        ical = self.generate_ical(recipients)
        msg.attach(
            filename='invite.ics',
            content_type='text/calendar',
            data=ical,
            headers=[('method', 'REQUEST')]
        )
        mail.send(msg)
