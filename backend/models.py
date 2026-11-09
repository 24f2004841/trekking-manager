import uuid
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    """
    Unified User model encompassing Admin, Trek Staff, and Trekkers.
    Supports deactivation, blacklisting, and role-based access control.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)

    active = db.Column(db.Boolean(), default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean(), default=False, nullable=False)

    # Required for Flask-Security session / token invalidation
    fs_uniquifier = db.Column(
        db.String(255), unique=True, nullable=False, default=lambda: uuid.uuid4().hex
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )

    roles = db.Column(db.String(10), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    staff_profile = db.relationship(
        "StaffProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    assigned_treks = db.relationship(
        "Trek", back_populates="assigned_staff", foreign_keys="Trek.assigned_staff_id"
    )
    bookings = db.relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


# --------------------------------------------------------------------------
# Staff Profile Model
# --------------------------------------------------------------------------


class StaffProfile(db.Model):
    """
    Profile extension for users with the Trek Staff role.
    """

    __tablename__ = "staff_profile"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(
        db.Integer(),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    experience_years = db.Column(db.Integer(), default=0, nullable=False)
    status = db.Column(
        db.String(50), default="Active", nullable=False
    )  # Active, On Leave, Inactive

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )

    user = db.relationship("User", back_populates="staff_profile")


# --------------------------------------------------------------------------
# Trek Route Model (was missing: Trek.route_id FK references trek_routes.id)
# --------------------------------------------------------------------------


class TrekRoute(db.Model):
    __tablename__ = "trek_routes"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    description = db.Column(db.Text(), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        nullable=False,
    )

    treks = db.relationship("Trek", back_populates="route")


# --------------------------------------------------------------------------
# Trek Event Model
# --------------------------------------------------------------------------


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer(), primary_key=True)
    route_id = db.Column(
        db.Integer(),
        db.ForeignKey("trek_routes.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False, index=True)
    difficulty = db.Column(db.String(50), nullable=False, index=True)
    duration_days = db.Column(db.Integer(), nullable=False)

    total_slots = db.Column(db.Integer(), nullable=False)
    available_slots = db.Column(db.Integer(), nullable=False)

    assigned_staff_id = db.Column(
        db.Integer(),
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status lifecycle: Pending -> Approved -> Open -> Closed -> Completed
    status = db.Column(db.String(50), default="Pending", nullable=False, index=True)

    start_date = db.Column(db.Date(), nullable=False, index=True)
    end_date = db.Column(db.Date(), nullable=False)

    instructions = db.Column(db.Text(), nullable=True)
    meeting_point = db.Column(db.Text(), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )

    __table_args__ = (
        db.CheckConstraint(
            "available_slots >= 0 AND available_slots <= total_slots",
            name="chk_available_slots_bound",
        ),
        db.CheckConstraint("end_date >= start_date", name="chk_valid_trek_dates"),
        db.CheckConstraint("total_slots > 0", name="chk_total_slots_positive"),
    )

    # Relationships
    route = db.relationship("TrekRoute", back_populates="treks")
    assigned_staff = db.relationship(
        "User", foreign_keys=[assigned_staff_id], back_populates="assigned_treks"
    )
    bookings = db.relationship(
        "Booking", back_populates="trek", cascade="all, delete-orphan"
    )


# --------------------------------------------------------------------------
# Booking Model
# --------------------------------------------------------------------------


class Booking(db.Model):
    """
    Record of a participant booking slots on a scheduled trek.
    Enforces uniqueness per user-trek pair to prevent duplicate bookings.
    """

    __tablename__ = "bookings"

    id = db.Column(db.Integer(), primary_key=True)
    booking_reference = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(
        db.Integer(),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trek_id = db.Column(
        db.Integer(),
        db.ForeignKey("treks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    num_slots = db.Column(db.Integer(), default=1, nullable=False)

    booking_date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(),
        nullable=False,
    )

    status = db.Column(db.String(50), default="Booked", nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek_booking"),
        db.CheckConstraint("num_slots > 0", name="chk_positive_slots"),
    )

    # Relationships
    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")
