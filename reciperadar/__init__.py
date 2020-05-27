from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from reciperadar.services.database import DB_URI


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.url_map.strict_slashes = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


import reciperadar.api.products
import reciperadar.api.recipes
