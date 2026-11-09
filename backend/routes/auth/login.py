from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, current_user, jwt_required

from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.full_name,
        "email": user.email,
        "role": user.roles,
    }


@auth_bp.post("/login")
def login():
    """Exchange credentials for a JWT. Used only when the client has no valid session."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    requested_role = data.get("role")  # UI hint only, never trusted

    user = User.query.filter_by(email=email).first()

    # Same message for unknown email and wrong password (no user enumeration)
    if user is None or not user.check_password(password):
        return jsonify(message="Invalid email or password"), 401

    if user.is_blacklisted or not user.active:
        return jsonify(message="This account has been disabled"), 403

    # The role comes from the database; the selected tab must match it.
    if requested_role:
        role_matches = requested_role == user.roles or (
            requested_role in ("user", "trekker") and user.roles in ("user", "trekker")
        )
        if not role_matches:
            return jsonify(message="Invalid email or password"), 401

    token = create_access_token(
        identity=user.id,
        additional_claims={
            "role": user.roles,
            "email": user.email,
        },  # UI convenience only
    )
    return jsonify(token=token, user=serialize_user(user))


@auth_bp.get("/me")
@jwt_required()
def me():
    """
    Called on app start when a token exists. The user is re-read from the
    database (see extensions._load_user), so blacklisting / deactivation /
    role changes take effect immediately, not when the JWT expires.
    """
    return jsonify(user=serialize_user(current_user))
