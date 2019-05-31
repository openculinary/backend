from datetime import datetime
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from icalendar import Calendar, Event, vCalAddress, vText
import smtplib
from uuid import uuid4


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

    def create_event(self, organizer, attendee):
        event = Event()
        event.add('summary', 'Test Meeting')
        event.add('dtstart', self.start_time)
        event.add('dtend', self.start_time + duration)
        event.add('uid', vText(uuid4()))
        event.add('organizer', organizer)
        event.add('attendee', attendee)
        return event

    def create_calendar(self, event):
        calendar = Calendar()
        calendar.add('prodid', '-//Recipe Radar//staging.reciperadar.com//')
        calendar.add('version', '2.0')
        calendar.add('method', 'REQUEST')
        calendar.add_component(event)
        return calendar

    def generate_ical(self, recipient):
        organizer = self.create_organizer()
        attendee = self.create_attendee(recipient)
        event = self.create_event(organizer, attendee)
        calendar = self.create_calendar(event)
        return calendar.to_ical()

    def generate_email_attachment(self, ical, filename='invite.ics'):
        att = MIMEBase('text', 'calendar', method='REQUEST', name=filename)
        att.set_type('text/calendar; charset=UTF-8; method=REQUEST; component=VEVENT')
        att.add_header('Content-Type', 'text/calendar')
        att.add_header('charset', 'UTF-8')
        att.add_header('component', 'VEVENT')
        att.add_header('method', 'REQUEST')
        att.add_header('Content-class', 'urn:content-classes:appointment')
        att.add_header('Content-ID', 'calendar_message')
        att.add_header('Content Description', filename)
        att.add_header('Filename', filename)
        att.add_header('Path', filename)
        att.set_payload(ical)
        encode_base64(att)
        return att

    def generate_email(self, recipient, attachment):
        message = MIMEMultipart()
        message['From'] = 'calendar@reciperadar.com'
        message['To']  = recipient
        message['Subject'] = self.title
        message.attach(attachment)
        return message

    def get_credentials(self):
        username = 'calendar@reciperadar.com'
        password = open('creds.swp', 'r').read()
        return username, password

    def send(self, recipient, message):
        username, password = self.get_credentials()
        server = smtplib.SMTP('smtp.gmail.com')
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(username, recipient, message.as_string())
        server.close()

    def send_reminders(self, recipients):
        for recipient in recipients:
            ical = self.generate_ical(recipient)
            att = self.generate_email_attachment(ical)
            email = self.generate_email(recipient, att)
            self.send(recipient, email)
