"""
app.py — Application factory for Expert Panel Recommendation System
====================================================================
Run with:
    python app.py
Or with Flask CLI:
    flask run
"""

from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

from config import Config
from models import db, Admin, Faculty, Department

mail = Mail()
migrate = Migrate()
login_manager = LoginManager()


# ── User loader (handles both Admin & Faculty) ─────────────────────────────────
@login_manager.user_loader
def load_user(user_id: str):
    if user_id.startswith("admin-"):
        return Admin.query.get(int(user_id.split("-", 1)[1]))
    elif user_id.startswith("faculty-"):
        return Faculty.query.get(int(user_id.split("-", 1)[1]))
    return None


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Initialize extensions ──────────────────────────────────────────────────
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # ── Register blueprints ────────────────────────────────────────────────────
    from routes.admin_routes import admin_bp
    from routes.faculty_routes import faculty_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(faculty_bp)

    # ── Main / root routes ─────────────────────────────────────────────────────
    from flask import Blueprint
    main_bp = Blueprint("main", __name__)

    @main_bp.route("/")
    def index():
        return render_template("index.html")

    app.register_blueprint(main_bp)

    # ── Create tables & seed admin ─────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app: Flask):
    """Create the default admin account if none exists."""
    if Admin.query.count() == 0:
        admin = Admin(
            username=app.config["ADMIN_USERNAME"],
            email=app.config["ADMIN_EMAIL"],
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(f"[SEED] Admin created: username='{app.config['ADMIN_USERNAME']}' "
              f"password='{app.config['ADMIN_PASSWORD']}'")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
