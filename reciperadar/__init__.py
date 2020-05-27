from flask import Flask

from reciperadar.services.database import DB_URI


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.url_map.strict_slashes = False


import reciperadar.api.products
import reciperadar.api.recipes
