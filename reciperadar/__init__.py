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
        'autoflush': False
    })
    # TODO: Remove workaround required for sqlalchemy + pg8000 v1.16.6
    # https://github.com/sqlalchemy/sqlalchemy/issues/5645#issuecomment-707879323
    db.engine.dialect.description_encoding = None
    return db


app = create_app()
db = create_db(app)
migrate = Migrate(app, db)


import reciperadar.api.domains
import reciperadar.api.products
import reciperadar.api.recipes
