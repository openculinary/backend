from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI='postgresql+pg8000://api@postgresql/api',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app, session_options={
    'autoflush': False
})
migrate = Migrate(app, db)


import reciperadar.api.products
import reciperadar.api.recipes
