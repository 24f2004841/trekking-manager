import re
import uuid

from flask import Blueprint, jsonify, request

from extensions import db
from models import StaffProfile, User
from routes.admin.common import TREKKER_ROLES, admin_required, like_pattern

people_bp = Blueprint("admin_people", __name__, url_prefix="/api/admin")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
STAFF_STATUSES = ("Active", "On Leave", "Inactive")
MIN_STAFF_PASSWORD = 8


def serialize_person(u: User) -> dict:
    data = {
        "id": u.id,
        "name": u.full_name,
        "username": u.username,
        "email": u.email,
        "contact": u.contact_number,
        "active": u.active,
        "blacklisted": u.is_blacklisted,
    }
    if u.roles == "staff":
        profile = u.staff_profile
        data["experience_years"] = profile.experience_years if profile else 0
        data["staff_status"] = profile.status if profile else None
    return data


def _search(query, q: str):
    if not q:
        return query
    pattern = like_pattern(q)
    return query.filter(
        db.or_(
            User.full_name.ilike(pattern, escape="\\"),
            User.email.ilike(pattern, escape="\\"),
            User.username.ilike(pattern, escape="\\"),
            User.contact_number.ilike(pattern, escape="\\"),
        )
    )


def _set_blacklist(user_id: int, roles: tuple):
    user = User.query.filter(User.id == user_id, User.roles.in_(roles)).first()
    if user is None:
        return jsonify(message="Account not found"), 404
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("blacklisted"), bool):
        return jsonify(message="'blacklisted' must be true or false"), 400
    user.is_blacklisted = data["blacklisted"]
    db.session.commit()
    return jsonify(serialize_person(user))


# ---- Users (Trekkers) ----------------------------------------------------


@people_bp.get("/users")
@admin_required
def list_users():
    query = User.query.filter(User.roles.in_(TREKKER_ROLES))
    query = _search(query, (request.args.get("q") or "").strip())
    return jsonify([serialize_person(u) for u in query.order_by(User.id)])


@people_bp.patch("/users/<int:user_id>/blacklist")
@admin_required
def blacklist_user(user_id: int):
    return _set_blacklist(user_id, TREKKER_ROLES)


# ---- Trekking Staff ------------------------------------------------------


@people_bp.get("/staff")
@admin_required
def list_staff():
    query = User.query.options(db.joinedload(User.staff_profile)).filter(
        User.roles == "staff"
    )
    query = _search(query, (request.args.get("q") or "").strip())
    return jsonify([serialize_person(u) for u in query.order_by(User.id)])


@people_bp.post("/staff")
@admin_required
def create_staff():
    data = request.get_json(silent=True) or {}

    full_name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    contact = (data.get("contact") or "").strip() or None
    password = data.get("password") or ""
    status = data.get("status") or "Active"
    experience = data.get("experience")
    if experience in (None, ""):
        experience = 0

    if not full_name:
        return jsonify(message="Full name is required"), 400
    if not email or not EMAIL_REGEX.match(email):
        return jsonify(message="A valid email is required"), 400
    if len(password) < MIN_STAFF_PASSWORD:
        return (
            jsonify(
                message=f"Password must be at least {MIN_STAFF_PASSWORD} characters long"
            ),
            400,
        )
    if status not in STAFF_STATUSES:
        return jsonify(
            message=f"Status must be one of: {', '.join(STAFF_STATUSES)}"
        ), 400
    if (
        isinstance(experience, bool)
        or not isinstance(experience, int)
        or experience < 0
    ):
        return jsonify(message="Experience must be a non-negative whole number"), 400

    if User.query.filter_by(email=email).first():
        return jsonify(message="An account with this email already exists"), 409

    base = re.sub(r"[^\w.-]", "", email.split("@")[0])[:90] or "staff"
    username, suffix = base, 1
    while User.query.filter_by(username=username).first():
        username = f"{base[:85]}_{suffix}"
        suffix += 1

    user = User(
        email=email,
        username=username,
        full_name=full_name,
        contact_number=contact,
        roles="staff",
        active=True,
        is_blacklisted=False,
        fs_uniquifier=uuid.uuid4().hex,
    )
    user.set_password(password)
    user.staff_profile = StaffProfile(experience_years=experience, status=status)

    db.session.add(user)
    db.session.commit()
    return jsonify(serialize_person(user)), 201


@people_bp.patch("/staff/<int:user_id>/blacklist")
@admin_required
def blacklist_staff(user_id: int):
    return _set_blacklist(user_id, ("staff",))
