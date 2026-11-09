from functools import wraps

from flask import jsonify
from flask_jwt_extended import current_user, jwt_required

# Accounts that belong to the "Users (Trekkers)" admin page. Login treats
# "user" as an alias of "trekker", so both are listed here.
TREKKER_ROLES = ("trekker", "user")


def admin_required(fn):
    """
    JWT must be valid (see extensions._load_user) AND the user's role, read
    from the database rather than the token, must be 'admin'.
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if current_user.roles != "admin":
            return jsonify(message="Admin access required"), 403
        return fn(*args, **kwargs)

    return wrapper


def like_pattern(q: str) -> str:
    """Build a case-insensitive LIKE pattern, escaping wildcard characters."""
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def iso(value):
    return value.isoformat() if value else None
