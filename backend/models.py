import uuid
from datetime import date, datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    Unified User model encompassing Admin, Trek Staff, and Trekkers.
    Supports deactivation, blacklisting, and role-based access control.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)

    # Status flags
    active = db.Column(db.Boolean(), default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean(), default=False, nullable=False)

    # Required for Flask-Security session / token invalidation
    fs_uniquifier = db.Column(
        db.String(255), unique=True, nullable=False, default=lambda: uuid.uuid4().hex
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
    )
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
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    @property
    def is_admin(self) -> bool:
        return any(role.name.lower() == "admin" for role in self.roles)

    @property
    def is_staff(self) -> bool:
        return any(role.name.lower() == "staff" for role in self.roles)

    @property
    def is_trekker(self) -> bool:
        return any(role.name.lower() in ("user", "trekker") for role in self.roles)

    def has_role(self, role_name: str) -> bool:
        return any(role.name.lower() == role_name.lower() for role in self.roles)

    def to_dict(self, include_profile=True):
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "contact_number": self.contact_number,
            "active": self.active,
            "is_blacklisted": self.is_blacklisted,
            "roles": [r.name for r in self.roles],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_profile and self.staff_profile:
            data["staff_profile"] = self.staff_profile.to_dict()
        return data

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


# --------------------------------------------------------------------------
# Staff Profile Model
# --------------------------------------------------------------------------


class StaffProfile(db.Model):
    """
    Profile extension for users with the Trek Staff role.
    """

    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(
        db.Integer(),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    experience_years = db.Column(db.Integer(), default=0, nullable=False)
    certifications = db.Column(db.Text(), nullable=True)
    emergency_contact = db.Column(db.String(50), nullable=True)
    status = db.Column(
        db.String(50), default="Active", nullable=False
    )  # Active, On Leave, Inactive
    bio = db.Column(db.Text(), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", back_populates="staff_profile")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "experience_years": self.experience_years,
            "certifications": self.certifications,
            "emergency_contact": self.emergency_contact,
            "status": self.status,
            "bio": self.bio,
        }

    def __repr__(self):
        return f"<StaffProfile UserID: {self.user_id}>"


# --------------------------------------------------------------------------
# Trek Route Model
# --------------------------------------------------------------------------


class TrekRoute(db.Model):
    """
    Defines general trekking routes that can be created and managed by Admin.
    """

    __tablename__ = "trek_routes"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    origin = db.Column(db.String(150), nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)  # Easy, Moderate, Hard
    distance_km = db.Column(db.Float(), nullable=True)
    altitude_gain_meters = db.Column(db.Integer(), nullable=True)
    base_duration_days = db.Column(db.Integer(), nullable=False)
    best_season = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text(), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    treks = db.relationship(
        "Trek", back_populates="route", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "origin": self.origin,
            "destination": self.destination,
            "difficulty": self.difficulty,
            "distance_km": self.distance_km,
            "altitude_gain_meters": self.altitude_gain_meters,
            "base_duration_days": self.base_duration_days,
            "best_season": self.best_season,
            "description": self.description,
        }

    def __repr__(self):
        return f"<TrekRoute {self.name}>"


# --------------------------------------------------------------------------
# Trek Event Model
# --------------------------------------------------------------------------


class Trek(db.Model):
    """
    A scheduled trekking event managed by staff and open to bookings by trekkers.
    """

    __tablename__ = "treks"

    id = db.Column(db.Integer(), primary_key=True)
    route_id = db.Column(
        db.Integer(),
        db.ForeignKey("trek_routes.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False, index=True)
    difficulty = db.Column(
        db.String(50), nullable=False, index=True
    )  # Easy, Moderate, Hard
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

    price = db.Column(db.Float(), default=0.0, nullable=False)
    itinerary = db.Column(db.Text(), nullable=True)
    meeting_point = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
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

    @property
    def is_open_for_booking(self) -> bool:
        return (
            self.status == "Open"
            and self.available_slots > 0
            and self.start_date > date.today()
        )

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty,
            "duration_days": self.duration_days,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff_name": self.assigned_staff.full_name
            if self.assigned_staff
            else None,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "price": self.price,
            "itinerary": self.itinerary,
            "meeting_point": self.meeting_point,
            "is_open_for_booking": self.is_open_for_booking,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Trek {self.name} [{self.status}] Slots: {self.available_slots}/{self.total_slots}>"


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

    booking_date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    num_slots = db.Column(db.Integer(), default=1, nullable=False)
    total_amount = db.Column(db.Float(), nullable=False)

    # Status: Booked, Cancelled, Completed
    status = db.Column(db.String(50), default="Booked", nullable=False, index=True)
    # Payment Status: Pending, Paid, Refunded, Failed
    payment_status = db.Column(db.String(50), default="Paid", nullable=False)

    emergency_contact = db.Column(db.String(100), nullable=True)
    special_notes = db.Column(db.Text(), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek_booking"),
        db.CheckConstraint("num_slots > 0", name="chk_positive_slots"),
    )

    # Relationships
    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "booking_reference": self.booking_reference,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.name if self.trek else None,
            "trek_location": self.trek.location if self.trek else None,
            "trek_start_date": self.trek.start_date.isoformat()
            if self.trek and self.trek.start_date
            else None,
            "trek_end_date": self.trek.end_date.isoformat()
            if self.trek and self.trek.end_date
            else None,
            "booking_date": self.booking_date.isoformat()
            if self.booking_date
            else None,
            "num_slots": self.num_slots,
            "total_amount": self.total_amount,
            "status": self.status,
            "payment_status": self.payment_status,
            "emergency_contact": self.emergency_contact,
            "special_notes": self.special_notes,
        }

    def __repr__(self):
        return f"<Booking {self.booking_reference} - User {self.user_id} - Trek {self.trek_id} [{self.status}]>"


# --------------------------------------------------------------------------
# Programmatic Initialization & Admin Seeding
# --------------------------------------------------------------------------


def init_db(
    app, admin_email="admin@trekking.org", admin_password="AdminSecurePassword123!"
):
    """
    Creates tables programmatically (as required by the specification)
    and guarantees the pre-existing superuser Admin account exists.
    """
    with app.app_context():
        db.create_all()

        # Seed roles
        default_roles = {
            "admin": "Application superuser with global privileges",
            "staff": "Trek coordinator and operational manager",
            "trekker": "Standard participant who registers and books treks",
        }
        for role_name, role_desc in default_roles.items():
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name, description=role_desc))
        db.session.commit()

        # Seed programmatically created Admin account (No admin self-registration allowed)
        admin_role = Role.query.filter_by(name="admin").first()
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                username="admin",
                full_name="System Administrator",
                contact_number="+91-9999999999",
                active=True,
                is_blacklisted=False,
            )
            admin_user.set_password(admin_password)
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
