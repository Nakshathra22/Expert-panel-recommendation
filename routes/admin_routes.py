"""
routes/admin_routes.py — All admin blueprint routes
=====================================================
Endpoints:
  /admin/login          GET/POST  – Admin login
  /admin/logout         GET       – Admin logout
  /admin/dashboard      GET       – Dashboard with KPI cards
  /admin/faculty        GET       – List all faculty
  /admin/faculty/add    GET/POST  – Add a single faculty
  /admin/faculty/<id>/edit       – Edit faculty record
  /admin/faculty/<id>/delete     – Delete faculty record
  /admin/departments    GET       – List departments
  /admin/departments/add         – Add department
  /admin/departments/<id>/delete – Delete department
  /admin/courses        GET       – List courses
  /admin/courses/add    GET/POST  – Add course
  /admin/courses/<id>/delete     – Delete course
  /admin/requests       GET       – Manage all panel requests
  /admin/requests/send  POST      – Send invitations for a course
  /admin/requests/<id>/remind    – Send reminder
  /admin/requests/<id>/replace   – Choose replacement for declined
  /admin/panels         GET       – View finalized panels
  /admin/panels/<id>/finalize    – Finalize a panel
  /admin/reports/<id>   GET       – Download PDF report
  /admin/reports/all    GET       – Download consolidated PDF
  /admin/reports/excel  GET       – Download Excel report
  /admin/logs           GET       – View activity log
  /admin/import         POST      – Import faculty from CSV/Excel
"""

import secrets
from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, session, send_file, current_app, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import io
import os

from models import (
    db, Admin, Department, Course, Faculty,
    PanelRequest, ExpertPanel, PanelMember, ActivityLog
)
from utils.email_utils import (
    generate_token, send_panel_request_email,
    send_reminder_email, send_acceptance_email
)
from utils.report_utils import (
    generate_panel_pdf, generate_all_panels_pdf, generate_excel_report
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Helper: log activity ───────────────────────────────────────────────────────
def log_action(action: str, details: str = ""):
    admin_id = current_user.id if current_user.is_authenticated else None
    entry = ActivityLog(
        admin_id=admin_id,
        action=action,
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(entry)
    db.session.commit()


def admin_only(f):
    """Decorator: ensure logged-in user is an Admin instance."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user._get_current_object(), Admin):
            flash("Admin access required.", "danger")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


# ── Auth ───────────────────────────────────────────────────────────────────────
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), Admin):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            log_action("Admin Login", f"Admin '{username}' logged in")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
@admin_only
def logout():
    log_action("Admin Logout")
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin.login"))


# ── Dashboard ──────────────────────────────────────────────────────────────────
@admin_bp.route("/dashboard")
@login_required
@admin_only
def dashboard():
    stats = {
        "total_faculty": Faculty.query.filter_by(is_active=True).count(),
        "total_departments": Department.query.count(),
        "total_courses": Course.query.count(),
        "pending_requests": PanelRequest.query.filter_by(status="pending").count(),
        "accepted_requests": PanelRequest.query.filter_by(status="accepted").count(),
        "declined_requests": PanelRequest.query.filter_by(status="declined").count(),
        "finalized_panels": ExpertPanel.query.count(),
        "courses_pending": Course.query.filter_by(status="pending").count(),
        "courses_in_progress": Course.query.filter_by(status="in_progress").count(),
        "courses_finalized": Course.query.filter_by(status="finalized").count(),
    }
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    recent_requests = (
        PanelRequest.query
        .order_by(PanelRequest.sent_at.desc())
        .limit(8)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_logs=recent_logs,
        recent_requests=recent_requests,
    )


# ── Faculty Management ─────────────────────────────────────────────────────────
@admin_bp.route("/faculty")
@login_required
@admin_only
def faculty_list():
    dept_filter = request.args.get("dept", "all")
    query = Faculty.query.filter_by(is_active=True)
    if dept_filter != "all":
        query = query.filter_by(department_id=int(dept_filter))
    faculty = query.order_by(Faculty.name).all()
    departments = Department.query.order_by(Department.name).all()
    return render_template("admin/faculty_list.html",
                           faculty=faculty, departments=departments,
                           dept_filter=dept_filter)


@admin_bp.route("/faculty/add", methods=["GET", "POST"])
@login_required
@admin_only
def add_faculty():
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        # Enforce college domain restriction
        if not (email.endswith("@kongu.edu") or email.endswith("@kongu.ac.in")):
            flash("Only faculty with @kongu.edu or @kongu.ac.in email addresses can be registered.", "danger")
            return render_template("admin/faculty_form.html", departments=departments, action="add")

        if Faculty.query.filter_by(email=email).first():
            flash("A faculty with this email already exists.", "warning")
            return render_template("admin/faculty_form.html", departments=departments, action="add")

        f = Faculty(
            name=request.form.get("name", "").strip(),
            email=email,
            designation=request.form.get("designation", "").strip() or None,
            years_of_experience=int(request.form.get("years_of_experience", 0)),
            area_of_expertise=request.form.get("area_of_expertise", "").strip() or None,
            department_id=int(request.form.get("department_id")),
        )
        db.session.add(f)
        db.session.commit()
        log_action("Add Faculty", f"Added faculty '{f.name}' ({f.email})")
        flash(f"Faculty '{f.name}' added successfully.", "success")
        return redirect(url_for("admin.faculty_list"))

    return render_template("admin/faculty_form.html", departments=departments, action="add")


@admin_bp.route("/faculty/<int:fid>/edit", methods=["GET", "POST"])
@login_required
@admin_only
def edit_faculty(fid: int):
    f = Faculty.query.get_or_404(fid)
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        f.name = request.form.get("name", f.name).strip()
        f.designation = request.form.get("designation", "").strip() or None
        f.years_of_experience = int(request.form.get("years_of_experience", f.years_of_experience))
        f.area_of_expertise = request.form.get("area_of_expertise", "").strip() or None
        f.department_id = int(request.form.get("department_id", f.department_id))
        db.session.commit()
        log_action("Edit Faculty", f"Edited faculty '{f.name}' (id={fid})")
        flash(f"Faculty '{f.name}' updated.", "success")
        return redirect(url_for("admin.faculty_list"))
    return render_template("admin/faculty_form.html", faculty=f, departments=departments, action="edit")


@admin_bp.route("/faculty/<int:fid>/delete", methods=["POST"])
@login_required
@admin_only
def delete_faculty(fid: int):
    f = Faculty.query.get_or_404(fid)
    name = f.name
    f.is_active = False  # Soft delete
    db.session.commit()
    log_action("Delete Faculty", f"Soft-deleted faculty '{name}' (id={fid})")
    flash(f"Faculty '{name}' removed.", "warning")
    return redirect(url_for("admin.faculty_list"))


# ── Import Faculty from CSV/Excel ──────────────────────────────────────────────
@admin_bp.route("/faculty/import", methods=["POST"])
@login_required
@admin_only
def import_faculty():
    file = request.files.get("dataset_file")
    if not file or file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("admin.faculty_list"))

    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    default_dept = request.form.get("default_dept", "").strip() or None
    try:
        from utils.dataset_loader import load_dataset
        summary = load_dataset(filepath, default_dept_name=default_dept)
        log_action(
            "Import Faculty Dataset",
            f"File={filename} inserted={summary['inserted']} updated={summary['updated']} "
            f"skipped={summary['skipped']} errors={len(summary['errors'])}"
        )
        flash(
            f"Import complete: {summary['inserted']} inserted, "
            f"{summary['updated']} updated, {summary['skipped']} skipped, "
            f"{len(summary['errors'])} errors.",
            "success" if not summary["errors"] else "warning"
        )
    except Exception as e:
        flash(f"Import failed: {e}", "danger")

    return redirect(url_for("admin.faculty_list"))


# ── Department Management ──────────────────────────────────────────────────────
@admin_bp.route("/departments")
@login_required
@admin_only
def departments():
    depts = Department.query.order_by(Department.name).all()
    return render_template("admin/departments.html", departments=depts)


@admin_bp.route("/departments/add", methods=["POST"])
@login_required
@admin_only
def add_department():
    name = request.form.get("name", "").strip()
    code = request.form.get("short_code", "").strip().upper()
    if not name or not code:
        flash("Department name and code are required.", "danger")
        return redirect(url_for("admin.departments"))
    if Department.query.filter_by(name=name).first():
        flash("Department already exists.", "warning")
        return redirect(url_for("admin.departments"))
    dept = Department(name=name, short_code=code)
    db.session.add(dept)
    db.session.commit()
    log_action("Add Department", f"'{name}' ({code})")
    flash(f"Department '{name}' added.", "success")
    return redirect(url_for("admin.departments"))


@admin_bp.route("/departments/<int:did>/delete", methods=["POST"])
@login_required
@admin_only
def delete_department(did: int):
    dept = Department.query.get_or_404(did)
    if dept.faculty.count() > 0 or dept.courses.count() > 0:
        flash("Cannot delete department with existing faculty or courses.", "danger")
        return redirect(url_for("admin.departments"))
    name = dept.name
    db.session.delete(dept)
    db.session.commit()
    log_action("Delete Department", f"Deleted '{name}'")
    flash(f"Department '{name}' deleted.", "warning")
    return redirect(url_for("admin.departments"))


# ── Course Management ──────────────────────────────────────────────────────────
@admin_bp.route("/courses")
@login_required
@admin_only
def courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    departments = Department.query.order_by(Department.name).all()
    return render_template("admin/courses.html", courses=all_courses, departments=departments)


@admin_bp.route("/courses/add", methods=["POST"])
@login_required
@admin_only
def add_course():
    code = request.form.get("code", "").strip().upper()
    if Course.query.filter_by(code=code).first():
        flash("Course code already exists.", "warning")
        return redirect(url_for("admin.courses"))
    c = Course(
        name=request.form.get("name", "").strip(),
        code=code,
        semester=request.form.get("semester", "").strip() or None,
        academic_year=request.form.get("academic_year", "").strip() or None,
        department_id=int(request.form.get("department_id")),
    )
    db.session.add(c)
    db.session.commit()
    log_action("Add Course", f"'{c.name}' ({c.code})")
    flash(f"Course '{c.name}' added.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/<int:cid>/delete", methods=["POST"])
@login_required
@admin_only
def delete_course(cid: int):
    c = Course.query.get_or_404(cid)
    if c.status == "finalized":
        flash("Cannot delete a finalized course.", "danger")
        return redirect(url_for("admin.courses"))
    name = c.name
    db.session.delete(c)
    db.session.commit()
    log_action("Delete Course", f"Deleted '{name}'")
    flash(f"Course '{name}' deleted.", "warning")
    return redirect(url_for("admin.courses"))


# ── Panel Request Management ───────────────────────────────────────────────────
@admin_bp.route("/requests")
@login_required
@admin_only
def manage_requests():
    courses = Course.query.filter(Course.status != "finalized").order_by(Course.name).all()
    all_requests = PanelRequest.query.order_by(PanelRequest.sent_at.desc()).all()
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        "admin/manage_requests.html",
        courses=courses, all_requests=all_requests, departments=departments
    )


@admin_bp.route("/requests/send", methods=["POST"])
@login_required
@admin_only
def send_requests():
    """
    Send panel invitations.
    Form fields: course_id, internal_ids[] (4), external_ids[] (3)
    """
    course_id = int(request.form.get("course_id"))
    course = Course.query.get_or_404(course_id)

    internal_ids = request.form.getlist("internal_ids[]")
    external_ids = request.form.getlist("external_ids[]")

    cfg = current_app.config
    if len(internal_ids) != cfg["INTERNAL_FACULTY_COUNT"]:
        flash(f"Please select exactly {cfg['INTERNAL_FACULTY_COUNT']} internal faculty.", "danger")
        return redirect(url_for("admin.manage_requests"))
    if len(external_ids) != cfg["EXTERNAL_FACULTY_COUNT"]:
        flash(f"Please select exactly {cfg['EXTERNAL_FACULTY_COUNT']} external faculty.", "danger")
        return redirect(url_for("admin.manage_requests"))

    max_courses = cfg.get("MAX_COURSES_PER_FACULTY", 2)
    for fid in internal_ids + external_ids:
        f = Faculty.query.get(int(fid))
        if f and f.assigned_courses_count >= max_courses:
            flash(f"Faculty '{f.name}' is already assigned to the maximum limit of {max_courses} courses.", "danger")
            return redirect(url_for("admin.manage_requests"))

    sent_count = 0
    for fid in internal_ids:
        sent_count += _send_or_skip(int(fid), course, "internal")
    for fid in external_ids:
        sent_count += _send_or_skip(int(fid), course, "external")

    course.status = "in_progress"
    db.session.commit()
    log_action("Send Panel Requests", f"Course={course.code} sent={sent_count}")
    flash(f"{sent_count} invitation(s) sent for '{course.name}'.", "success")
    return redirect(url_for("admin.manage_requests"))


def _send_or_skip(faculty_id: int, course, role: str) -> int:
    """Create a PanelRequest and send email. Returns 1 on success, 0 on skip."""
    existing = PanelRequest.query.filter_by(
        faculty_id=faculty_id, course_id=course.id, role=role
    ).filter(PanelRequest.status != "declined").first()
    if existing:
        return 0

    token = generate_token()
    req = PanelRequest(
        faculty_id=faculty_id,
        course_id=course.id,
        role=role,
        token=token,
        status="pending",
    )
    db.session.add(req)
    db.session.flush()
    success = send_panel_request_email(req)
    if not success:
        req.status = "email_failed"
    return 1


@admin_bp.route("/requests/<int:rid>/remind", methods=["POST"])
@login_required
@admin_only
def remind_faculty(rid: int):
    req = PanelRequest.query.get_or_404(rid)
    if req.status not in ["pending", "email_failed"]:
        flash("Can only remind pending requests.", "warning")
        return redirect(url_for("admin.manage_requests"))
    ok = send_reminder_email(req) if req.status == "pending" else send_panel_request_email(req)
    if ok:
        req.status = "pending"
        db.session.commit()
    flash("Invitation / Reminder sent." if ok else "Failed to send email. Check your SMTP settings in .env.", "success" if ok else "danger")
    log_action("Send Reminder / Retry", f"Request id={rid}")
    return redirect(url_for("admin.manage_requests"))


@admin_bp.route("/requests/<int:rid>/replace", methods=["GET", "POST"])
@login_required
@admin_only
def replace_faculty(rid: int):
    """Choose a replacement for a faculty who declined."""
    original_req = PanelRequest.query.get_or_404(rid)
    if original_req.status != "declined":
        flash("Can only replace declined requests.", "warning")
        return redirect(url_for("admin.manage_requests"))

    course = original_req.course
    dept = course.department

    if request.method == "POST":
        new_fid = int(request.form.get("new_faculty_id"))
        token = generate_token()
        new_req = PanelRequest(
            faculty_id=new_fid,
            course_id=course.id,
            role=original_req.role,
            token=token,
            status="pending",
        )
        db.session.add(new_req)
        db.session.flush()
        send_panel_request_email(new_req)
        db.session.commit()
        log_action("Replace Faculty", f"Request id={rid} replaced by faculty id={new_fid}")
        flash("Replacement invitation sent.", "success")
        return redirect(url_for("admin.manage_requests"))

    # GET: show replacement picker
    # Exclude already-invited faculty for this course
    invited_ids = [
        r.faculty_id for r in PanelRequest.query.filter_by(course_id=course.id).all()
    ]
    if original_req.role == "internal":
        candidates = Faculty.query.filter(
            Faculty.is_active == True,
            Faculty.department_id == dept.id,
            ~Faculty.id.in_(invited_ids),
        ).order_by(Faculty.years_of_experience.desc()).all()
    else:
        candidates = Faculty.query.filter(
            Faculty.is_active == True,
            Faculty.department_id != dept.id,
            ~Faculty.id.in_(invited_ids),
        ).order_by(Faculty.years_of_experience.desc()).all()

    max_courses = current_app.config.get("MAX_COURSES_PER_FACULTY", 2)
    candidates = [c for c in candidates if c.assigned_courses_count < max_courses]

    return render_template(
        "admin/replace_faculty.html",
        original_req=original_req,
        candidates=candidates,
    )


# ── Expert Panel View & Finalization ──────────────────────────────────────────
@admin_bp.route("/panels")
@login_required
@admin_only
def view_panels():
    panels = ExpertPanel.query.order_by(ExpertPanel.finalized_at.desc()).all()
    # Courses ready to finalize (in_progress, enough accepted)
    ready_courses = []
    for c in Course.query.filter_by(status="in_progress").all():
        accepted = PanelRequest.query.filter_by(course_id=c.id, status="accepted").count()
        total_needed = (
            current_app.config["INTERNAL_FACULTY_COUNT"] +
            current_app.config["EXTERNAL_FACULTY_COUNT"]
        )
        if accepted >= total_needed:
            ready_courses.append(c)
    return render_template("admin/panels.html", panels=panels, ready_courses=ready_courses)


@admin_bp.route("/panels/<int:cid>/finalize", methods=["POST"])
@login_required
@admin_only
def finalize_panel(cid: int):
    course = Course.query.get_or_404(cid)
    if course.panel:
        flash("Panel already finalized.", "info")
        return redirect(url_for("admin.view_panels"))

    accepted_requests = PanelRequest.query.filter_by(
        course_id=cid, status="accepted"
    ).all()
    panel = ExpertPanel(
        course_id=cid,
        finalized_by=current_user.id,
        notes=request.form.get("notes", ""),
    )
    db.session.add(panel)
    db.session.flush()

    for req in accepted_requests:
        pm = PanelMember(panel_id=panel.id, faculty_id=req.faculty_id, role=req.role)
        db.session.add(pm)

    course.status = "finalized"
    db.session.commit()
    log_action("Finalize Panel", f"Course={course.code} panel_id={panel.id}")
    flash(f"Panel for '{course.name}' finalized.", "success")
    return redirect(url_for("admin.view_panels"))


# ── Reports ────────────────────────────────────────────────────────────────────
@admin_bp.route("/reports/<int:pid>/pdf")
@login_required
@admin_only
def report_pdf(pid: int):
    panel = ExpertPanel.query.get_or_404(pid)
    pdf_bytes = generate_panel_pdf(panel)
    filename = f"panel_{panel.course.code}.pdf"
    log_action("Download PDF Report", f"panel_id={pid} course={panel.course.code}")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@admin_bp.route("/reports/all/pdf")
@login_required
@admin_only
def report_all_pdf():
    panels = ExpertPanel.query.all()
    if not panels:
        flash("No finalized panels to report.", "info")
        return redirect(url_for("admin.view_panels"))
    pdf_bytes = generate_all_panels_pdf(panels)
    log_action("Download Consolidated PDF Report")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="all_expert_panels.pdf",
    )


@admin_bp.route("/reports/all/excel")
@login_required
@admin_only
def report_excel():
    panels = ExpertPanel.query.all()
    if not panels:
        flash("No finalized panels to export.", "info")
        return redirect(url_for("admin.view_panels"))
    excel_bytes = generate_excel_report(panels)
    log_action("Download Excel Report")
    return send_file(
        io.BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="expert_panels.xlsx",
    )


# ── Activity Log ───────────────────────────────────────────────────────────────
@admin_bp.route("/logs")
@login_required
@admin_only
def activity_logs():
    page = request.args.get("page", 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=30
    )
    return render_template("admin/activity_logs.html", logs=logs)


# ── AJAX endpoint: get faculty for course dept ─────────────────────────────────
@admin_bp.route("/api/faculty_for_course/<int:cid>")
@login_required
@admin_only
def api_faculty_for_course(cid: int):
    course = Course.query.get_or_404(cid)
    dept_id = course.department_id
    internal = Faculty.query.filter_by(department_id=dept_id, is_active=True).order_by(
        Faculty.years_of_experience.desc()
    ).all()
    external = Faculty.query.filter(
        Faculty.department_id != dept_id, Faculty.is_active == True
    ).order_by(Faculty.years_of_experience.desc()).all()

    max_courses = current_app.config.get("MAX_COURSES_PER_FACULTY", 2)

    def serialize(f):
        c_count = f.assigned_courses_count
        return {
            "id": f.id, "name": f.name, "email": f.email,
            "designation": f.designation, "years_of_experience": f.years_of_experience,
            "area_of_expertise": f.area_of_expertise,
            "department": f.department.name,
            "assigned_count": c_count,
            "is_max_reached": c_count >= max_courses,
            "max_limit": max_courses,
        }

    return jsonify({
        "internal": [serialize(f) for f in internal],
        "external": [serialize(f) for f in external],
        "course": {"name": course.name, "code": course.code, "dept": course.department.name},
    })
