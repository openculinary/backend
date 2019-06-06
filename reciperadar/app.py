from base58 import b58encode
from datetime import datetime
from dateutil import parser
from flask import Flask, jsonify, request
from flask_mail import Mail
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
import os
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError
from uuid import uuid4
from validate_email import validate_email

from reciperadar.models.course import Course
from reciperadar.models.email import Email
from reciperadar.models.ingredient import Ingredient
from reciperadar.models.recipe import Recipe
from reciperadar.models.reminder import Reminder
from reciperadar.models.reminder_attendee import ReminderAttendee
from reciperadar.services.calendar import get_calendar_api
from reciperadar.services.database import Database
from reciperadar.services.emails import issue_verification_token

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
)
mail = Mail(app)


@app.route('/api/courses')
def courses():
    prefix = request.args.get('pre')
    results = Course().autosuggest(prefix)
    return jsonify([result['name'] for result in results])


@app.route('/api/ingredients')
def ingredients():
    prefix = request.args.get('pre')
    results = Ingredient().autosuggest(prefix)
    return jsonify([result['name'] for result in results])


@app.route('/api/recipes/search')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    results = Recipe().search(include, exclude)
    return jsonify(results)


@app.route('/api/recipes/<recipe_id>/reminder', methods=['POST'])
def recipe_reminder(recipe_id):
    emails = request.form.getlist('email[]')

    session = Database().get_session()
    for email in emails:
        if not validate_email(email, check_mx=True):
            return jsonify({'error': 'invalid_email'}), 400
        if not session.query(Email) \
           .filter(Email.email == email) \
           .first():
            return jsonify({'error': 'unregistered_email'}), 400
        if not session.query(Email) \
           .filter(Email.email == email) \
           .filter(Email.verified_at.isnot(None)) \
           .first():
            return jsonify({'error': 'unverified_email'}), 400

    dt = request.form.get('dt')
    dt = parser.parse(dt)

    tz = request.form.get('tz')
    try:
        timezone(tz)
    except UnknownTimeZoneError:
        return jsonify({'error': 'invalid_timezone'}), 400

    recipe = Recipe().get_by_id(recipe_id)
    reminder = Reminder.from_scheduled_recipe(
        recipe=recipe,
        start_time=dt,
        timezone=tz,
    )
    reminder.send(emails)

    return jsonify({
        'title': reminder.summary,
        'start_time': reminder.start_time.isoformat(),
        'end_time': reminder.end_time.isoformat(),
        'recipients': emails,
    })


@app.route('/api/emails/register')
def register_email():
    email = request.args.get('email')
    if not validate_email(email, check_mx=True):
        return jsonify({'error': 'invalid_email'}), 400

    token = b58encode(uuid4().bytes).decode('utf-8')
    record = Email(
        email=email,
        token=token
    )

    session = Database().get_session()
    session.add(record)
    try:
        session.commit()
        issue_verification_token.delay(email, token)
    except IntegrityError:
        pass
    return jsonify({})


@app.route('/api/emails/verify')
def verify_email():
    token = request.args.get('token')

    session = Database().get_session()
    email = session.query(Email).filter(Email.token == token).first()
    if email:
        email.verified_at = datetime.utcnow()
        session.commit()
    return jsonify({'token': token})


@app.route('/webhooks/calendar', methods=['POST'])
def calendar_webhooks():
    session = Database().get_session()
    updated_min = session.query(func.max(Reminder.updated)).scalar()

    calendar = get_calendar_api()
    events = calendar.events().list(
        calendarId='primary',
        updatedMin=updated_min.isoformat() + 'Z'
    ).execute()

    for event in events['items']:
        reminder = Reminder.from_webhook(event)
        session.query(ReminderAttendee).filter(
            ReminderAttendee.reminder_id == reminder.id
        ).delete()
        session.query(Reminder).filter(
            Reminder.id == reminder.id
        ).delete()

        session.add(reminder)
        session.flush()
        session.add_all(reminder.attendees)
    session.commit()
    return jsonify({})
