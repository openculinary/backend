from base58 import b58encode
from datetime import datetime
from flask import abort, jsonify, redirect, request
from sqlalchemy.exc import IntegrityError
from urllib.parse import unquote
from uuid import uuid4
from validate_email import validate_email

from reciperadar import app
from reciperadar.models.email import Email
from reciperadar.services.database import Database
from reciperadar.workers.emails import issue_verification_token


@app.route('/api/emails/register', methods=['POST'])
def register_email():
    email = request.form.get('email')
    email = unquote(email)

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
    session.close()
    return jsonify({})


@app.route('/api/emails/verify')
def verify_email():
    token = request.args.get('token')

    session = Database().get_session()
    email = session.query(Email).filter(Email.token == token).first()
    if not email:
        return abort(404)
    if not email.verified_at:
        email.verified_at = datetime.utcnow()
        session.commit()
    session.close()
    return redirect('/#action=verified', code=301)
