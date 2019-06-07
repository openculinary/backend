from dateutil import parser
from flask import jsonify, request
from sqlalchemy.sql.expression import func
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError
from urllib.parse import unquote
from validate_email import validate_email

from reciperadar.app import app
from reciperadar.models.email import Email
from reciperadar.models.recipe import Recipe
from reciperadar.models.reminder import Reminder
from reciperadar.services.calendar import get_calendar_api
from reciperadar.services.database import Database


@app.route('/api/recipes/<recipe_id>/reminder', methods=['POST'])
def recipe_reminder(recipe_id):
    emails = request.form.getlist('email[]')
    emails = [unquote(email) for email in emails]

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


@app.route('/webhooks/calendar', methods=['POST'])
def calendar_webhooks():
    session = Database().get_session()
    updated_min = session.query(func.max(Reminder.updated)).scalar()
    if updated_min:
        updated_min = updated_min.isoformat() + 'Z'

    calendar = get_calendar_api()
    events = calendar.events().list(
        calendarId='primary',
        updatedMin=updated_min
    ).execute()

    for event in events['items']:
        reminder = Reminder.from_webhook(event)
        session.query(Reminder).filter_by(id=reminder.id).delete()
        session.add(reminder)
    session.commit()
    return jsonify({})
