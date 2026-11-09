from flask import Blueprint, jsonify
from routes.admin.bookings import serialize_booking

from models import Booking, Trek, User
from routes.admin.common import TREKKER_ROLES, admin_required

dashboard_bp = Blueprint("admin_dashboard", __name__, url_prefix="/api/admin")


@dashboard_bp.get("/dashboard")
@admin_required
def dashboard():
    recent = Booking.query.order_by(
        Booking.booking_date.desc(), Booking.id.desc()
    ).limit(5)
    return jsonify(
        totals={
            "treks": Trek.query.count(),
            "users": User.query.filter(User.roles.in_(TREKKER_ROLES)).count(),
            "staff": User.query.filter_by(roles="staff").count(),
            "bookings": Booking.query.count(),
        },
        recentBookings=[serialize_booking(b) for b in recent],
    )
