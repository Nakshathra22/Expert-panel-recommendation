
"""
utils/email_utils.py — Email sending helpers for Expert Panel System
=====================================================================
Functions:
  send_panel_request_email  – invite a faculty member to join a panel
  send_acceptance_email     – confirm acceptance & send login credentials
  send_decline_notification – notify admin that a faculty declined
  send_reminder_email       – reminder to faculty who haven't responded
"""

import secrets
from datetime import datetime, timezone
from flask import current_app, url_for
from flask_mail import Message
from models import db, PanelRequest


def _mail():
    """Lazy-import mail extension to avoid circular imports."""
    from app import mail
    return mail


def generate_token() -> str:
    """Return a 48-character URL-safe token."""
    return secrets.token_urlsafe(36)


def get_external_url(endpoint: str, **values) -> str:
    """Generate external URL using BASE_URL if configured, else fallback to url_for."""
    base_url = current_app.config.get("BASE_URL", "").strip().rstrip("/")
    if base_url:
        path = url_for(endpoint, **values)
        return f"{base_url}{path}"
    return url_for(endpoint, _external=True, **values)


def send_panel_request_email(request_obj: PanelRequest) -> bool:
    """
    Send an invitation email to a faculty member.
    Returns True on success, False on failure.
    """
    faculty = request_obj.faculty
    course = request_obj.course
    department = course.department
    college = current_app.config["COLLEGE_NAME"]
    role_label = "Internal" if request_obj.role == "internal" else "External"

    accept_url = get_external_url(
        "faculty.respond_request",
        token=request_obj.token,
        action="accept",
    )
    decline_url = get_external_url(
        "faculty.respond_request",
        token=request_obj.token,
        action="decline",
    )

    subject = f"[{college}] Expert Panel Invitation – {course.name}"
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
      <div style="background:#1a237e;color:#fff;padding:20px 30px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;">Expert Panel Invitation</h2>
        <p style="margin:4px 0 0;">{college}</p>
      </div>
      <div style="background:#f9f9f9;padding:25px 30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
        <p>Dear <strong>{faculty.name}</strong>,</p>
        <p>You are invited to serve as an <strong>{role_label} Expert</strong> on the
           panel for:</p>
        <table style="width:100%;border-collapse:collapse;margin:15px 0;">
          <tr><td style="padding:8px;font-weight:bold;width:40%;background:#e8eaf6;">Course</td>
              <td style="padding:8px;background:#fff;">{course.name} ({course.code})</td></tr>
          <tr><td style="padding:8px;font-weight:bold;background:#e8eaf6;">Department</td>
              <td style="padding:8px;background:#fff;">{department.name}</td></tr>
          <tr><td style="padding:8px;font-weight:bold;background:#e8eaf6;">Semester</td>
              <td style="padding:8px;background:#fff;">{course.semester or 'N/A'}</td></tr>
          <tr><td style="padding:8px;font-weight:bold;background:#e8eaf6;">Academic Year</td>
              <td style="padding:8px;background:#fff;">{course.academic_year or 'N/A'}</td></tr>
          <tr><td style="padding:8px;font-weight:bold;background:#e8eaf6;">Your Role</td>
              <td style="padding:8px;background:#fff;">{role_label} Expert</td></tr>
        </table>
        <p>Please respond using the buttons below:</p>
        <div style="text-align:center;margin:25px 0;">
          <a href="{accept_url}"
             style="background:#2e7d32;color:#fff;padding:12px 28px;border-radius:5px;
                    text-decoration:none;font-size:16px;margin-right:12px;">
            ✅ Accept
          </a>
          <a href="{decline_url}"
             style="background:#c62828;color:#fff;padding:12px 28px;border-radius:5px;
                    text-decoration:none;font-size:16px;">
            ❌ Decline
          </a>
        </div>
        <p style="font-size:13px;color:#777;">
          This link is unique to you. Please do not share it.<br>
          If you have questions, contact the admin.
        </p>
      </div>
    </body></html>
    """

    try:
        msg = Message(subject=subject, recipients=[faculty.email], html=html_body)
        _mail().send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email send failed for {faculty.email}: {e}")
        return False


def send_acceptance_email(request_obj: PanelRequest, temp_password: str) -> bool:
    """
    Send login credentials to a faculty who accepted the invitation.
    """
    faculty = request_obj.faculty
    course = request_obj.course
    college = current_app.config["COLLEGE_NAME"]
    login_url = get_external_url("faculty.login")

    subject = f"[{college}] Panel Acceptance Confirmed – Login Credentials"
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
      <div style="background:#1a237e;color:#fff;padding:20px 30px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;">Welcome to the Expert Panel</h2>
        <p style="margin:4px 0 0;">{college}</p>
      </div>
      <div style="background:#f9f9f9;padding:25px 30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
        <p>Dear <strong>{faculty.name}</strong>,</p>
        <p>Thank you for accepting the invitation for <strong>{course.name}</strong>.</p>
        <p>Your portal login credentials:</p>
        <table style="width:100%;border-collapse:collapse;margin:15px 0;">
          <tr><td style="padding:8px;font-weight:bold;width:40%;background:#e8eaf6;">Email / Username</td>
              <td style="padding:8px;background:#fff;">{faculty.email}</td></tr>
          <tr><td style="padding:8px;font-weight:bold;background:#e8eaf6;">Temporary Password</td>
              <td style="padding:8px;background:#fff;font-family:monospace;font-size:16px;">{temp_password}</td></tr>
        </table>
        <div style="text-align:center;margin:25px 0;">
          <a href="{login_url}"
             style="background:#1a237e;color:#fff;padding:12px 28px;border-radius:5px;
                    text-decoration:none;font-size:16px;">
            🔐 Login to Portal
          </a>
        </div>
        <p style="color:#c62828;font-size:13px;">Please change your password after first login.</p>
      </div>
    </body></html>
    """

    try:
        msg = Message(subject=subject, recipients=[faculty.email], html=html_body)
        _mail().send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Acceptance email failed for {faculty.email}: {e}")
        return False


def send_decline_notification(request_obj: PanelRequest, admin_email: str) -> bool:
    """
    Notify admin that a faculty has declined.
    """
    faculty = request_obj.faculty
    course = request_obj.course
    college = current_app.config["COLLEGE_NAME"]

    subject = f"[{college}] Faculty Declined Panel Invitation – Action Required"
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
      <div style="background:#b71c1c;color:#fff;padding:20px 30px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;">Panel Invitation Declined</h2>
      </div>
      <div style="background:#f9f9f9;padding:25px 30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
        <p><strong>{faculty.name}</strong> ({faculty.email}) has
           <span style="color:#c62828;font-weight:bold;">declined</span> the expert panel invitation for:</p>
        <p>Course: <strong>{course.name} ({course.code})</strong></p>
        <p>Role: <strong>{'Internal' if request_obj.role == 'internal' else 'External'}</strong></p>
        {f"<p>Reason: {request_obj.decline_reason}</p>" if request_obj.decline_reason else ""}
        <p>Please log in to the admin portal to select a replacement faculty.</p>
      </div>
    </body></html>
    """

    try:
        msg = Message(subject=subject, recipients=[admin_email], html=html_body)
        _mail().send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Decline notification failed: {e}")
        return False


def send_reminder_email(request_obj: PanelRequest) -> bool:
    """
    Send a reminder to a faculty who hasn't responded yet.
    """
    faculty = request_obj.faculty
    course = request_obj.course
    college = current_app.config["COLLEGE_NAME"]

    accept_url = get_external_url(
        "faculty.respond_request",
        token=request_obj.token,
        action="accept",
    )
    decline_url = get_external_url(
        "faculty.respond_request",
        token=request_obj.token,
        action="decline",
    )

    subject = f"[{college}] REMINDER: Expert Panel Invitation – {course.name}"
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
      <div style="background:#e65100;color:#fff;padding:20px 30px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;">⏰ Reminder: Expert Panel Invitation</h2>
      </div>
      <div style="background:#f9f9f9;padding:25px 30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
        <p>Dear <strong>{faculty.name}</strong>,</p>
        <p>This is a reminder that you have a <strong>pending invitation</strong> for the expert panel of
           <strong>{course.name}</strong>. Please respond at your earliest convenience.</p>
        <div style="text-align:center;margin:25px 0;">
          <a href="{accept_url}"
             style="background:#2e7d32;color:#fff;padding:12px 28px;border-radius:5px;
                    text-decoration:none;font-size:16px;margin-right:12px;">✅ Accept</a>
          <a href="{decline_url}"
             style="background:#c62828;color:#fff;padding:12px 28px;border-radius:5px;
                    text-decoration:none;font-size:16px;">❌ Decline</a>
        </div>
      </div>
    </body></html>
    """

    try:
        msg = Message(subject=subject, recipients=[faculty.email], html=html_body)
        _mail().send(msg)
        request_obj.reminder_sent = True
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Reminder email failed for {faculty.email}: {e}")
        return False
