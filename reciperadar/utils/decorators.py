from functools import wraps

from flask import abort, request


def internal(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        external = request.headers.get('x-reciperadar-external')
        if external:
            return abort(403)
        return f(*args, **kwargs)
    return decorated
