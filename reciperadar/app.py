from flask import Flask
from flask_mail import Mail
import os


app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
)
mail = Mail(app)


import reciperadar.api.emails
import reciperadar.api.recipes
import reciperadar.api.reminders
import reciperadar.api.search
