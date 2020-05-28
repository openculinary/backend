from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI='postgresql+pg8000://api@postgresql/api',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app, session_options={
    'autoflush': False
})


import reciperadar.api.products
import reciperadar.api.recipes
