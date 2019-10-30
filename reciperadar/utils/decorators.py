from functools import wraps

from flask import abort, request
from ipaddress import ip_address


def internal(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for and not ip_address(forwarded_for).is_private:
            return abort(403)
        return f(*args, **kwargs)
    return decorated
