from flask_mail import Message
from icalendar import Calendar, Event, vCalAddress, vText
from uuid import uuid4


class MealReminder(object):

    def __init__(self, title, start_time, duration, recipients):
        self.title = title
        self.start_time = start_time
        self.duration = duration
        self.recipients = recipients

    def create_organizer(self):
        organizer = vCalAddress('MAILTO:calendar@reciperadar.com')
        organizer.params['cn'] = vText('Recipe Radar')
        organizer.params['role'] = vText('CHAIR')
        return organizer

    def create_attendee(self, recipient):
        attendee = vCalAddress('MAILTO:{}'.format(recipient))
        attendee.params['role'] = vText('REQ-PARTICIPANT')
        return attendee

    def create_event(self):
        event = Event()
        event.add('summary', self.title)
        event.add('dtstart', self.start_time)
        event.add('dtend', self.start_time + self.duration)
        event.add('uid', vText(uuid4()))

        organizer = self.create_organizer()
        event.add('organizer', organizer)

        for recipient in self.recipients:
            attendee = self.create_attendee(recipient)
            event.add('attendee', attendee)

        return event

    def create_calendar(self):
        calendar = Calendar()
        calendar.add('prodid', '-//Recipe Radar//staging.reciperadar.com//')
        calendar.add('version', '2.0')
        calendar.add('method', 'REQUEST')

        event = self.create_event()
        calendar.add_component(event)

        return calendar

    def send(self):
        if not self.recipients:
            return

        message = Message(
            subject=self.title,
            sender='calendar@reciperadar.com',
            recipients=self.recipients
        )
        calendar = self.create_calendar()
        message.attach(
            filename='invite.ics',
            content_type='text/calendar',
            data=calendar.to_ical(),
            headers=[('method', 'REQUEST')]
        )

        from reciperadar.app import mail
        mail.send(message)
