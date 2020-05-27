from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from reciperadar.services.database import DB_URI


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.url_map.strict_slashes = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app, origins=[
    r'^https://\w+.reciperadar.com$',
    r'^http://localhost$',
    r'^http://192.168.\d+.\d+$',
])


import reciperadar.api.products
import reciperadar.api.recipes
