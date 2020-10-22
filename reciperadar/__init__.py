from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def create_app(db_uri='postgresql+pg8000://api@postgresql/api'):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    return app


def create_db(app):
    db = SQLAlchemy(app, session_options={
        'autoflush': False,
        'expire_on_commit': False,
    })
    return db


app = create_app()
db = create_db(app)
migrate = Migrate(app, db)


import reciperadar.api.domains
import reciperadar.api.products
import reciperadar.api.recipes
