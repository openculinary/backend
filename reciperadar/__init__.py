from flask import Flask
from flask.sessions import SessionMixin
from flask_admin import Admin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"autoflush": False})


def create_app(db_uri="postgresql+pg8000://backend@postgresql/backend"):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI=db_uri)
    return app


class EphemeralSession(dict, SessionMixin):
    def open_session(self, app, request):
        return EphemeralSession()

    def is_null_session(self, obj):
        return True


app = create_app()
app.session_interface = EphemeralSession()
migrate = Migrate(app, db)
admin_app = Admin(app)
db.init_app(app)


import reciperadar.admin.products
import reciperadar.api.domains
import reciperadar.api.products
import reciperadar.api.recipes
