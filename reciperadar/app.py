from base58 import b58encode
from datetime import datetime, timedelta
from dateutil import parser
from flask import Flask, jsonify, request
from flask_mail import Mail
from sqlalchemy.exc import IntegrityError
import os
from uuid import uuid4
from validate_email import validate_email

from reciperadar.course import Course
from reciperadar.email import Email
from reciperadar.ingredient import Ingredient
from reciperadar.recipe import Recipe
from reciperadar.reminders import MealReminder
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
        if not validate_email(email):
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

    recipe = Recipe().get_by_id(recipe_id)
    reminder = MealReminder(
        title=recipe['name'],
        start_time=dt,
        duration=timedelta(minutes=recipe['time']),
        recipients=emails
    )
    reminder.send()

    return jsonify({
        'title': reminder.title,
        'start_time': reminder.start_time.isoformat(),
        'duration': int(reminder.duration.total_seconds() / 60),
        'emails': emails,
    })


@app.route('/api/emails/register')
def register_email():
    email = request.args.get('email')
    if not validate_email(email):
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
