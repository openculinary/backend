from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from reciperadar.services.database import DB_URI


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app)


import reciperadar.api.products
import reciperadar.api.recipes
