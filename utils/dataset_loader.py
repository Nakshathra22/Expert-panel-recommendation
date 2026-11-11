"""
utils/dataset_loader.py
========================
Utility to import faculty data from CSV or Excel into the database.
Run this script directly OR call load_dataset() from app context.

Expected columns (case-insensitive, flexible naming):
  name, email, designation, years_of_experience / experience,
  area_of_expertise / expertise, department

Usage (CLI):
  python utils/dataset_loader.py --file faculty_data.csv --dept "Computer Science"
"""

import sys
import os
import argparse
import pandas as pd

# Allow running as a standalone script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


COL_MAP = {
    # Possible column name variants → normalized name
    "name": "name",
    "faculty name": "name",
    "staff name": "name",
    "email": "email",
    "mail": "email",
    "email id": "email",
    "mail id": "email",
    "designation": "designation",
    "post": "designation",
    "years_of_experience": "years_of_experience",
    "years of experience": "years_of_experience",
    "experience": "years_of_experience",
    "exp": "years_of_experience",
    "area_of_expertise": "area_of_expertise",
    "area of expertise": "area_of_expertise",
    "expertise": "area_of_expertise",
    "specialization": "area_of_expertise",
    "department": "department",
    "dept": "department",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    renamed = {}
    for col in df.columns:
        if col in COL_MAP:
            renamed[col] = COL_MAP[col]
    df = df.rename(columns=renamed)
    return df


def load_dataset(filepath: str, default_dept_name: str | None = None,
                 create_dept: bool = True) -> dict:
    """
    Load faculty data from a CSV or Excel file into the database.

    Parameters
    ----------
    filepath        : path to .csv / .xlsx / .xls file
    default_dept_name : department name to use when 'department' column is absent
    create_dept     : if True, auto-create departments that don't exist yet

    Returns a summary dict: {inserted, updated, skipped, errors}
    """
    from app import create_app
    from models import db, Faculty, Department

    app = create_app()
    with app.app_context():
        # ── Read file ──────────────────────────────────────────────────────────
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(filepath)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        df = _normalize_columns(df)

        required = {"name", "email"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Dataset is missing required columns: {missing}")

        # ── Process rows ───────────────────────────────────────────────────────
        summary = {"inserted": 0, "updated": 0, "skipped": 0, "errors": []}

        for idx, row in df.iterrows():
            try:
                name = str(row.get("name", "")).strip()
                email = str(row.get("email", "")).strip().lower()
                if not name or not email or "@" not in email:
                    summary["skipped"] += 1
                    continue

                # Enforce domain restriction
                if not (email.endswith("@kongu.edu") or email.endswith("@kongu.ac.in")):
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {idx}: {email} ignored (only @kongu.edu or @kongu.ac.in allowed)")
                    continue

                # Department resolution
                dept_name = (
                    str(row.get("department", "")).strip()
                    if "department" in df.columns and pd.notna(row.get("department"))
                    else default_dept_name
                )
                if not dept_name:
                    summary["errors"].append(f"Row {idx}: no department for {email}")
                    continue

                dept = Department.query.filter(
                    db.func.lower(Department.name) == dept_name.lower()
                ).first()
                if not dept:
                    if create_dept:
                        dept = Department(
                            name=dept_name,
                            short_code=dept_name[:6].upper().replace(" ", "")
                        )
                        db.session.add(dept)
                        db.session.flush()
                    else:
                        summary["errors"].append(
                            f"Row {idx}: department '{dept_name}' not found"
                        )
                        continue

                # Faculty upsert
                faculty = Faculty.query.filter_by(email=email).first()
                if faculty:
                    # Update existing record
                    faculty.name = name
                    faculty.designation = str(row.get("designation", faculty.designation or "")).strip() or None
                    if "years_of_experience" in df.columns and pd.notna(row.get("years_of_experience")):
                        faculty.years_of_experience = int(row["years_of_experience"])
                    if "area_of_expertise" in df.columns and pd.notna(row.get("area_of_expertise")):
                        faculty.area_of_expertise = str(row["area_of_expertise"]).strip()
                    faculty.department_id = dept.id
                    summary["updated"] += 1
                else:
                    faculty = Faculty(
                        name=name,
                        email=email,
                        designation=str(row.get("designation", "")).strip() or None,
                        years_of_experience=int(row["years_of_experience"])
                            if "years_of_experience" in df.columns and pd.notna(row.get("years_of_experience"))
                            else 0,
                        area_of_expertise=str(row["area_of_expertise"]).strip()
                            if "area_of_expertise" in df.columns and pd.notna(row.get("area_of_expertise"))
                            else None,
                        department_id=dept.id,
                    )
                    db.session.add(faculty)
                    summary["inserted"] += 1

            except Exception as e:
                summary["errors"].append(f"Row {idx}: {e}")
                db.session.rollback()

        db.session.commit()
        return summary


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load faculty dataset into Expert Panel DB")
    parser.add_argument("--file", required=True, help="Path to CSV or Excel file")
    parser.add_argument("--dept", default=None, help="Default department name (if not in file)")
    parser.add_argument("--no-create-dept", action="store_true",
                        help="Do not auto-create missing departments")
    args = parser.parse_args()

    result = load_dataset(
        filepath=args.file,
        default_dept_name=args.dept,
        create_dept=not args.no_create_dept,
    )
    print("\n=== Dataset Load Summary ===")
    print(f"  Inserted : {result['inserted']}")
    print(f"  Updated  : {result['updated']}")
    print(f"  Skipped  : {result['skipped']}")
    if result["errors"]:
        print(f"  Errors   : {len(result['errors'])}")
        for err in result["errors"]:
            print(f"    - {err}")
    else:
        print("  Errors   : 0")
    print("============================\n")
