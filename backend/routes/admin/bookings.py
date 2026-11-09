from flask import Blueprint, jsonify

from extensions import db
from models import Booking
from routes.admin.common import admin_required, iso

bookings_bp = Blueprint("admin_bookings", __name__, url_prefix="/api/admin")


def serialize_booking(b: Booking) -> dict:
    return {
        "id": b.id,
        "booking_reference": b.booking_reference,
        "user_id": b.user_id,
        "user": b.user.full_name,
        "trek_id": b.trek_id,
        "trek": b.trek.name,
        "num_slots": b.num_slots,
        "booking_date": iso(b.booking_date),
        "status": b.status,
    }


@bookings_bp.get("/bookings")
@admin_required
def list_bookings():
    rows = (
        Booking.query.options(db.joinedload(Booking.user), db.joinedload(Booking.trek))
        .order_by(Booking.booking_date.desc(), Booking.id.desc())
        .all()
    )
    return jsonify([serialize_booking(b) for b in rows])
