from flask import Blueprint, jsonify, request

from extensions import db
from models import Trek, User
from routes.admin.common import admin_required, iso, like_pattern

treks_bp = Blueprint("admin_treks", __name__, url_prefix="/api/admin")


def serialize_trek(t: Trek) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration_days": t.duration_days,
        "total_slots": t.total_slots,
        "available_slots": t.available_slots,
        "status": t.status,
        "start_date": iso(t.start_date),
        "end_date": iso(t.end_date),
        "route": t.route.name if t.route else None,
        "assigned_staff_id": t.assigned_staff_id,
        "assigned_staff": t.assigned_staff.full_name if t.assigned_staff else None,
    }


@treks_bp.get("/treks")
@admin_required
def list_treks():
    q = (request.args.get("q") or "").strip()
    query = Trek.query.options(
        db.joinedload(Trek.route), db.joinedload(Trek.assigned_staff)
    )
    if q:
        pattern = like_pattern(q)
        query = query.outerjoin(User, Trek.assigned_staff_id == User.id).filter(
            db.or_(
                Trek.name.ilike(pattern, escape="\\"),
                Trek.location.ilike(pattern, escape="\\"),
                Trek.difficulty.ilike(pattern, escape="\\"),
                Trek.status.ilike(pattern, escape="\\"),
                User.full_name.ilike(pattern, escape="\\"),
            )
        )
    return jsonify(
        [serialize_trek(t) for t in query.order_by(Trek.start_date, Trek.id)]
    )


@treks_bp.delete("/treks/<int:trek_id>")
@admin_required
def delete_trek(trek_id: int):
    trek = db.session.get(Trek, trek_id)
    if trek is None:
        return jsonify(message="Trek not found"), 404
    db.session.delete(trek)  # bookings are removed via ORM cascade
    db.session.commit()
    return jsonify(message="Trek deleted")
