"""
utils/report_utils.py — PDF & Excel report generation
======================================================
Functions:
  generate_panel_pdf      – produce a PDF report for a finalized panel
  generate_all_panels_pdf – produce a consolidated PDF for all panels
  generate_excel_report   – produce an Excel workbook of all panel data
"""

import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from flask import current_app


_HEADER_COLOR = colors.HexColor("#1a237e")
_ALT_COLOR = colors.HexColor("#e8eaf6")
_ACCENT = colors.HexColor("#3949ab")


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Title2", fontSize=18, textColor=colors.white,
        alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="Sub", fontSize=11, textColor=colors.white,
        alignment=TA_CENTER, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="SectionHead", fontSize=13, textColor=_HEADER_COLOR,
        fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=12
    ))
    styles.add(ParagraphStyle(
        name="Body2", fontSize=10, spaceAfter=4
    ))
    return styles


def _draw_header(canvas, doc, college_name: str):
    """Draw a coloured header banner on every page."""
    canvas.saveState()
    w, h = doc.pagesize
    banner_h = 2.5 * cm
    canvas.setFillColor(_HEADER_COLOR)
    canvas.rect(0, h - banner_h, w, banner_h, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(w / 2, h - 1.6 * cm, college_name)
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(w / 2, h - 2.2 * cm, "Expert Panel Recommendation System")
    # Footer
    canvas.setFillColor(colors.grey)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 1 * cm, 0.8 * cm,
                           f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}  |  Page {doc.page}")
    canvas.restoreState()


def generate_panel_pdf(panel) -> bytes:
    """
    Generate a PDF for a single finalized ExpertPanel.
    Returns raw bytes.
    """
    college = current_app.config["COLLEGE_NAME"]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=3 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = _base_styles()
    story = []

    # Course info block
    course = panel.course
    dept = course.department
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Expert Panel Report", styles["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=_HEADER_COLOR))
    story.append(Spacer(1, 0.3 * cm))

    info_data = [
        ["Course Name", course.name],
        ["Course Code", course.code],
        ["Department", dept.name],
        ["Semester", course.semester or "—"],
        ["Academic Year", course.academic_year or "—"],
        ["Finalized On", panel.finalized_at.strftime("%d-%b-%Y %H:%M") if panel.finalized_at else "—"],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 11 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), _ALT_COLOR),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.6 * cm))

    # Panel members table
    story.append(Paragraph("Panel Members", styles["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=_HEADER_COLOR))
    story.append(Spacer(1, 0.3 * cm))

    header = ["#", "Name", "Department", "Designation", "Experience (Yrs)", "Expertise", "Role"]
    rows = [header]
    members = list(panel.members)
    for i, m in enumerate(members, 1):
        f = m.faculty
        rows.append([
            str(i),
            f.name,
            f.department.name,
            f.designation or "—",
            str(f.years_of_experience),
            f.area_of_expertise or "—",
            m.role.capitalize(),
        ])

    col_widths = [0.7 * cm, 3.5 * cm, 3 * cm, 2.8 * cm, 2.2 * cm, 3.5 * cm, 2 * cm]
    members_table = Table(rows, colWidths=col_widths, repeatRows=1)
    members_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _HEADER_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _ALT_COLOR]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (4, 0), (4, -1), "CENTER"),
    ]))
    story.append(members_table)

    if panel.notes:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(f"<b>Notes:</b> {panel.notes}", styles["Body2"]))

    doc.build(
        story,
        onFirstPage=lambda c, d: _draw_header(c, d, college),
        onLaterPages=lambda c, d: _draw_header(c, d, college),
    )
    return buffer.getvalue()


def generate_all_panels_pdf(panels: list) -> bytes:
    """
    Consolidated PDF for all finalized panels.
    """
    college = current_app.config["COLLEGE_NAME"]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        topMargin=3 * cm, bottomMargin=2 * cm,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm
    )
    styles = _base_styles()
    story = []

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("All Expert Panels – Consolidated Report", styles["SectionHead"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}",
        styles["Body2"]
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_HEADER_COLOR))
    story.append(Spacer(1, 0.4 * cm))

    header = ["Course", "Code", "Dept", "Faculty Name", "Designation", "Exp.", "Role"]
    for panel in panels:
        course = panel.course
        story.append(Paragraph(
            f"{course.name} ({course.code}) — {course.department.name}",
            styles["SectionHead"]
        ))
        rows = [header]
        for m in panel.members:
            f = m.faculty
            rows.append([
                course.name, course.code, course.department.short_code,
                f.name, f.designation or "—",
                str(f.years_of_experience), m.role.capitalize()
            ])
        t = Table(rows, colWidths=[5 * cm, 2.5 * cm, 3 * cm, 4 * cm, 3.5 * cm, 1.5 * cm, 2.5 * cm],
                  repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _HEADER_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _ALT_COLOR]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5 * cm))
        story.append(PageBreak())

    doc.build(
        story,
        onFirstPage=lambda c, d: _draw_header(c, d, college),
        onLaterPages=lambda c, d: _draw_header(c, d, college),
    )
    return buffer.getvalue()


def generate_excel_report(panels: list) -> bytes:
    """
    Generate an Excel workbook with one sheet per panel.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    header_fill = PatternFill("solid", fgColor="1a237e")
    alt_fill = PatternFill("solid", fgColor="e8eaf6")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    bold_font = Font(bold=True, size=10)
    thin = Side(style="thin", color="AAAAAA")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    college = current_app.config["COLLEGE_NAME"]

    for panel in panels:
        course = panel.course
        sheet_name = (course.code[:28] if len(course.code) > 28 else course.code)
        ws = wb.create_sheet(title=sheet_name)

        # Title rows
        ws.append([college])
        ws.append(["Expert Panel Report"])
        ws.append([])
        ws.append(["Course:", course.name, "", "Code:", course.code])
        ws.append(["Department:", course.department.name, "", "Semester:", course.semester or "—"])
        ws.append(["Academic Year:", course.academic_year or "—", "", "Finalized:",
                   panel.finalized_at.strftime("%d-%b-%Y") if panel.finalized_at else "—"])
        ws.append([])

        # Header row
        headers = ["#", "Name", "Email", "Department", "Designation",
                   "Years of Experience", "Area of Expertise", "Role"]
        ws.append(headers)
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=ws.max_row, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = border

        # Data rows
        for i, m in enumerate(panel.members, 1):
            f = m.faculty
            row_data = [
                i, f.name, f.email, f.department.name,
                f.designation or "—", f.years_of_experience,
                f.area_of_expertise or "—", m.role.capitalize()
            ]
            ws.append(row_data)
            fill = alt_fill if i % 2 == 0 else PatternFill("solid", fgColor="FFFFFF")
            for col_idx in range(1, len(row_data) + 1):
                cell = ws.cell(row=ws.max_row, column=col_idx)
                cell.fill = fill
                cell.border = border
                cell.alignment = Alignment(wrap_text=True)

        # Column widths
        for col in ws.columns:
            max_len = max((len(str(c.value)) if c.value else 0) for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
