from base58 import b58encode
from datetime import datetime
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
from reciperadar.services.database import Database

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


@app.route('/api/recipes')
def recipes():
    include = request.args.getlist('include[]')
    exclude = request.args.getlist('exclude[]')
    results = Recipe().search(include, exclude)
    return jsonify(results)


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
