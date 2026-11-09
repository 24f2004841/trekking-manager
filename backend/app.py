from flask import Flask, jsonify

from config import Config
from extensions import cors, db, jwt
from models import User


def init_db(app, admin_email=None, admin_password=None):
    """
    Creates tables programmatically (as required by the specification)
    and guarantees the pre-existing superuser Admin account exists.
    """
    admin_email = admin_email or app.config["ADMIN_EMAIL"]
    admin_password = admin_password or app.config["ADMIN_PASSWORD"]
    with app.app_context():
        db.create_all()

        # Seed programmatically created Admin account
        # (No admin self-registration allowed)
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                username="admin",
                full_name="System Administrator",
                contact_number="+91-9999999999",
                active=True,
                roles="admin",
                is_blacklisted=False,
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=["http://localhost:5173"], supports_credentials=True)

    init_db(app)

    from routes.admin.bookings import bookings_bp
    from routes.admin.dashboard import dashboard_bp
    from routes.admin.people import people_bp
    from routes.admin.treks import treks_bp
    from routes.auth.login import auth_bp
    from routes.auth.register import register_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(treks_bp)
    app.register_blueprint(people_bp)
    app.register_blueprint(bookings_bp)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/db-check")
    def db_check():
        """Verify backend <-> database connectivity."""
        try:
            counts = {
                "users": User.query.count(),
            }
            return jsonify(
                connected=True,
                database=app.config["SQLALCHEMY_DATABASE_URI"],
                counts=counts,
            )
        except Exception as exc:  # noqa: BLE001
            return jsonify(connected=False, error=str(exc)), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
