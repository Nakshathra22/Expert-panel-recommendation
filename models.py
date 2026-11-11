"""
models.py — SQLAlchemy ORM models for Expert Panel System
==========================================================
Tables:
  Admin           – system administrator accounts
  Department      – academic departments in the college
  Course          – courses that need an expert panel
  Faculty         – all faculty members (internal & external determined at runtime)
  PanelRequest    – invitation sent to a faculty member for a course panel
  ExpertPanel     – finalized panel composition for a course
  ActivityLog     – audit trail of admin actions
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ─────────────────────────── Admin ────────────────────────────────────────────
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # Flask-Login requires a unique string id
    def get_id(self) -> str:
        return f"admin-{self.id}"

    def __repr__(self) -> str:
        return f"<Admin {self.username}>"


# ────────────────────────── Department ────────────────────────────────────────
class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    short_code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    faculty = db.relationship("Faculty", back_populates="department", lazy="dynamic")
    courses = db.relationship("Course", back_populates="department", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Department {self.name}>"


# ──────────────────────────── Course ──────────────────────────────────────────
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    semester = db.Column(db.String(30))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    academic_year = db.Column(db.String(20))
    status = db.Column(
        db.String(20), default="pending"
    )  # pending | in_progress | finalized
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    department = db.relationship("Department", back_populates="courses")
    requests = db.relationship("PanelRequest", back_populates="course", lazy="dynamic")
    panel = db.relationship("ExpertPanel", back_populates="course", uselist=False)

    def __repr__(self) -> str:
        return f"<Course {self.code}: {self.name}>"


# ─────────────────────────── Faculty ──────────────────────────────────────────
class Faculty(UserMixin, db.Model):
    __tablename__ = "faculty"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    designation = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer, default=0)
    area_of_expertise = db.Column(db.Text)  # comma-separated tags
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    password_hash = db.Column(db.String(256))  # set only after acceptance
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    department = db.relationship("Department", back_populates="faculty")
    requests = db.relationship("PanelRequest", back_populates="faculty", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # Flask-Login requires a unique string id
    def get_id(self) -> str:
        return f"faculty-{self.id}"

    @property
    def expertise_list(self) -> list[str]:
        if not self.area_of_expertise:
            return []
        return [e.strip() for e in self.area_of_expertise.split(",") if e.strip()]

    @property
    def assigned_courses_count(self) -> int:
        """Count distinct courses where faculty is actively assigned or pending (not declined)."""
        return self.requests.filter(PanelRequest.status.in_(["pending", "accepted"])).count()

    def can_assign_more(self, max_limit: int = 2) -> bool:
        return self.assigned_courses_count < max_limit

    def __repr__(self) -> str:
        return f"<Faculty {self.name}>"


# ─────────────────────────── PanelRequest ─────────────────────────────────────
class PanelRequest(db.Model):
    __tablename__ = "panel_requests"

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # internal | external
    status = db.Column(db.String(20), default="pending")  # pending | accepted | declined
    token = db.Column(db.String(200), unique=True)  # unique token for email link
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    responded_at = db.Column(db.DateTime)
    decline_reason = db.Column(db.Text)
    reminder_sent = db.Column(db.Boolean, default=False)

    # Relationships
    faculty = db.relationship("Faculty", back_populates="requests")
    course = db.relationship("Course", back_populates="requests")

    def __repr__(self) -> str:
        return f"<PanelRequest faculty={self.faculty_id} course={self.course_id} status={self.status}>"


# ─────────────────────────── ExpertPanel ──────────────────────────────────────
class ExpertPanel(db.Model):
    __tablename__ = "expert_panels"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), unique=True, nullable=False)
    finalized_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    finalized_by = db.Column(db.Integer, db.ForeignKey("admins.id"))
    notes = db.Column(db.Text)

    # Relationships
    course = db.relationship("Course", back_populates="panel")
    members = db.relationship("PanelMember", back_populates="panel", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<ExpertPanel course={self.course_id}>"


class PanelMember(db.Model):
    __tablename__ = "panel_members"

    id = db.Column(db.Integer, primary_key=True)
    panel_id = db.Column(db.Integer, db.ForeignKey("expert_panels.id"), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # internal | external

    # Relationships
    panel = db.relationship("ExpertPanel", back_populates="members")
    faculty = db.relationship("Faculty")


# ─────────────────────────── ActivityLog ──────────────────────────────────────
class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"))
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address = db.Column(db.String(50))

    def __repr__(self) -> str:
        return f"<ActivityLog {self.action} @ {self.timestamp}>"
