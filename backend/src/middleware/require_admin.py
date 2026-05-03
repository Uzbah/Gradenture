from functools import wraps
from flask import jsonify, g


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user.get("role") not in ("admin", "super_admin"):
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated


def require_super_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user.get("role") != "super_admin":
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated
