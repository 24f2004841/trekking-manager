from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


@jwt.user_identity_loader
def _identity(user_id):
    return str(user_id)


@jwt.user_lookup_loader
def _load_user(_header, payload):
    """
    Runs on every @jwt_required() request. A valid signature is not enough:
    the user must still exist, be active and not be blacklisted. Returning
    None triggers `_user_lookup_failed` (401).
    """
    from models import User  # lazy import: models imports this module

    user = db.session.get(User, int(payload["sub"]))
    if user is None or not user.active or user.is_blacklisted:
        return None
    return user


@jwt.user_lookup_error_loader
def _user_lookup_failed(_header, _payload):
    return jsonify(message="Session is no longer valid"), 401


@jwt.expired_token_loader
def _expired(_header, _payload):
    return jsonify(message="Token expired"), 401


@jwt.invalid_token_loader
def _invalid(reason):
    return jsonify(message=reason), 401


@jwt.unauthorized_loader
def _missing(reason):
    return jsonify(message=reason), 401
