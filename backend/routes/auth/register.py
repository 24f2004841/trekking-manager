import re
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from extensions import db
from models import User
from routes.auth.login import serialize_user

register_bp = Blueprint("auth_register", __name__, url_prefix="/api/auth")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@register_bp.post("/register")
def register():
    """
    Register a new user (trekker).
    Staff accounts cannot be registered here because staff is created by admin
    with specialized profiles.
    """
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or data.get("name") or "").strip()
    username = (data.get("username") or "").strip()
    contact_number = (
        data.get("contact_number") or data.get("contact") or ""
    ).strip() or None

    # Validation
    if not email:
        return jsonify(message="Email is required"), 400

    if not EMAIL_REGEX.match(email):
        return jsonify(message="Invalid email format"), 400

    if not password:
        return jsonify(message="Password is required"), 400

    if len(password) < 6:
        return jsonify(message="Password must be at least 6 characters long"), 400

    if not full_name:
        return jsonify(message="Full name is required"), 400

    # Ensure email uniqueness
    if User.query.filter_by(email=email).first():
        return jsonify(message="An account with this email already exists"), 409

    # Handle username (provided or auto-derived from email)
    if username:
        if User.query.filter_by(username=username).first():
            return jsonify(message="Username is already taken"), 409
    else:
        base_username = re.sub(r"[^\w.-]", "", email.split("@")[0])[:90] or "user"
        username = base_username
        suffix = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username[:85]}_{suffix}"
            suffix += 1

    # Normal users get the 'trekker' role.
    # Self-registration of admin or staff accounts is disallowed.
    new_user = User(
        email=email,
        username=username,
        full_name=full_name,
        contact_number=contact_number,
        roles="trekker",
        active=True,
        is_blacklisted=False,
        fs_uniquifier=uuid.uuid4().hex,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    token = create_access_token(
        identity=new_user.id,
        additional_claims={
            "role": new_user.roles,
            "email": new_user.email,
        },
    )

    return (
        jsonify(
            message="User registered successfully",
            token=token,
            user=serialize_user(new_user),
        ),
        201,
    )
