"""
routes/faculty_routes.py — Faculty blueprint
=============================================
Endpoints:
  /faculty/login            GET/POST – Faculty login (email + password)
  /faculty/logout           GET      – Faculty logout
  /faculty/respond/<token>  GET      – Accept / Decline via email link
  /faculty/dashboard        GET      – Faculty home after login
  /faculty/profile          GET      – Faculty profile & assigned panels
  /faculty/change-password  POST     – Change password after first login
"""

import secrets
from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user

from models import db, Faculty, PanelRequest, ExpertPanel, PanelMember
from utils.email_utils import send_acceptance_email, send_decline_notification

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")


def faculty_only(f):
    """Decorator: ensure logged-in user is a Faculty instance."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(
            current_user._get_current_object(), Faculty
        ):
            flash("Please log in as a faculty member.", "danger")
            return redirect(url_for("faculty.login"))
        return f(*args, **kwargs)
    return decorated


# ── Auth ───────────────────────────────────────────────────────────────────────
@faculty_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), Faculty):
        return redirect(url_for("faculty.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Only faculty with @kongu.edu or @kongu.ac.in can access the portal
        if not (email.endswith("@kongu.edu") or email.endswith("@kongu.ac.in")):
            flash("Access denied. Only @kongu.edu or @kongu.ac.in accounts are permitted to log in.", "danger")
            return render_template("faculty/login.html")

        faculty = Faculty.query.filter_by(email=email, is_active=True).first()

        if not faculty:
            flash("No faculty account found with this email.", "danger")
            return render_template("faculty/login.html")

        # Only approved faculty can log in
        accepted_req = PanelRequest.query.filter_by(
            faculty_id=faculty.id, status="accepted"
        ).first()
        if not accepted_req:
            flash("Access denied. Your invitation has not been accepted yet.", "warning")
            return render_template("faculty/login.html")

        if faculty.check_password(password):
            login_user(faculty)
            return redirect(url_for("faculty.dashboard"))

        flash("Incorrect password.", "danger")

    return render_template("faculty/login.html")


@faculty_bp.route("/logout")
@login_required
@faculty_only
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("faculty.login"))


# ── Email Response (Accept / Decline) ─────────────────────────────────────────
@faculty_bp.route("/respond/<token>")
def respond_request(token: str):
    action = request.args.get("action", "")
    req = PanelRequest.query.filter_by(token=token).first()

    if not req:
        flash("Invalid or expired invitation link.", "danger")
        return render_template("faculty/respond.html", status="invalid")

    if req.status != "pending":
        return render_template("faculty/respond.html",
                               status=req.status, req=req)

    if action == "accept":
        req.status = "accepted"
        req.responded_at = datetime.now(timezone.utc)
        db.session.flush()

        # Generate temporary password and enable login
        temp_password = secrets.token_urlsafe(8)
        faculty = req.faculty
        if not faculty.password_hash:
            faculty.set_password(temp_password)

        db.session.commit()
        send_acceptance_email(req, temp_password)
        return render_template("faculty/respond.html", status="accepted",
                               req=req, temp_password=temp_password)

    elif action == "decline":
        if request.method == "GET":
            return render_template("faculty/decline_form.html", req=req, token=token)

    flash("Unknown action.", "danger")
    return redirect(url_for("main.index"))


@faculty_bp.route("/respond/<token>/confirm-decline", methods=["POST"])
def confirm_decline(token: str):
    req = PanelRequest.query.filter_by(token=token).first()
    if not req or req.status != "pending":
        flash("Invalid request.", "danger")
        return redirect(url_for("main.index"))

    req.status = "declined"
    req.responded_at = datetime.now(timezone.utc)
    req.decline_reason = request.form.get("reason", "").strip()
    db.session.commit()

    # Notify admin
    admin = __import__("models", fromlist=["Admin"]).Admin.query.first()
    if admin:
        send_decline_notification(req, admin.email)

    return render_template("faculty/respond.html", status="declined", req=req)


# ── Faculty Portal ─────────────────────────────────────────────────────────────
@faculty_bp.route("/dashboard")
@login_required
@faculty_only
def dashboard():
    faculty = current_user._get_current_object()
    accepted_requests = PanelRequest.query.filter_by(
        faculty_id=faculty.id, status="accepted"
    ).all()
    # Gather panel info
    panels_info = []
    for req in accepted_requests:
        course = req.course
        panel = ExpertPanel.query.filter_by(course_id=course.id).first()
        members = list(panel.members) if panel else []
        panels_info.append({
            "course": course,
            "role": req.role,
            "panel": panel,
            "members": members,
        })

    return render_template(
        "faculty/dashboard.html",
        faculty=faculty,
        panels_info=panels_info,
    )


@faculty_bp.route("/profile")
@login_required
@faculty_only
def profile():
    faculty = current_user._get_current_object()
    return render_template("faculty/profile.html", faculty=faculty)


@faculty_bp.route("/change-password", methods=["POST"])
@login_required
@faculty_only
def change_password():
    faculty = current_user._get_current_object()
    current_pw = request.form.get("current_password", "")
    new_pw = request.form.get("new_password", "")
    confirm_pw = request.form.get("confirm_password", "")

    if not faculty.check_password(current_pw):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("faculty.profile"))

    if new_pw != confirm_pw:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("faculty.profile"))

    if len(new_pw) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("faculty.profile"))

    faculty.set_password(new_pw)
    db.session.commit()
    flash("Password changed successfully.", "success")
    return redirect(url_for("faculty.profile"))
