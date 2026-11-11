"""
seed_demo.py — Populate the database with demo data for testing
===============================================================
Run once after app.py to get started quickly:
    python seed_demo.py
"""

from app import create_app
from models import db, Department, Faculty, Course

app = create_app()

with app.app_context():
    # ── Departments ────────────────────────────────────────────────────────────
    depts_data = [
        ("Computer Science and Engineering", "CSE"),
        ("Electronics and Communication Engineering", "ECE"),
        ("Mechanical Engineering", "MECH"),
        ("Information Technology", "IT"),
        ("Civil Engineering", "CIVIL"),
    ]

    depts = {}
    for name, code in depts_data:
        d = Department.query.filter_by(short_code=code).first()
        if not d:
            d = Department(name=name, short_code=code)
            db.session.add(d)
            db.session.flush()
        depts[code] = d

    # ── Faculty (CSE — internal) ───────────────────────────────────────────────
    cse_faculty = [
        ("Dr. A. Priya", "priya.a@college.edu", "Professor", 18, "Machine Learning, Deep Learning, AI"),
        ("Dr. B. Rajan", "rajan.b@college.edu", "Associate Professor", 12, "Data Science, Big Data, Python"),
        ("Prof. C. Meena", "meena.c@college.edu", "Assistant Professor", 7, "Computer Networks, Security"),
        ("Dr. D. Suresh", "suresh.d@college.edu", "Professor", 22, "Algorithms, Graph Theory, Optimization"),
        ("Prof. E. Kavitha", "kavitha.e@college.edu", "Assistant Professor", 5, "Cloud Computing, DevOps"),
        ("Dr. F. Kumar", "kumar.f@college.edu", "Associate Professor", 14, "Compiler Design, OS, Systems"),
    ]

    # ── Faculty (Other depts — external candidates) ────────────────────────────
    other_faculty = [
        ("Dr. G. Nair", "nair.g@college.edu", "Professor", 20, "Signal Processing, VLSI", "ECE"),
        ("Prof. H. Sharma", "sharma.h@college.edu", "Associate Professor", 10, "IoT, Embedded Systems", "ECE"),
        ("Dr. I. Venkat", "venkat.i@college.edu", "Professor", 16, "CAD/CAM, Robotics", "MECH"),
        ("Prof. J. Latha", "latha.j@college.edu", "Assistant Professor", 6, "Web Development, Databases", "IT"),
        ("Dr. K. Balan", "balan.k@college.edu", "Professor", 25, "Structural Analysis, FEM", "CIVIL"),
    ]

    for name, email, designation, exp, expertise in cse_faculty:
        if not Faculty.query.filter_by(email=email).first():
            f = Faculty(
                name=name, email=email, designation=designation,
                years_of_experience=exp, area_of_expertise=expertise,
                department_id=depts["CSE"].id
            )
            db.session.add(f)

    for name, email, designation, exp, expertise, dept_code in other_faculty:
        if not Faculty.query.filter_by(email=email).first():
            f = Faculty(
                name=name, email=email, designation=designation,
                years_of_experience=exp, area_of_expertise=expertise,
                department_id=depts[dept_code].id
            )
            db.session.add(f)

    # ── Courses ────────────────────────────────────────────────────────────────
    courses_data = [
        ("Artificial Intelligence", "CS601", "CSE", "VI", "2025-26"),
        ("Machine Learning", "CS602", "CSE", "VI", "2025-26"),
        ("Data Structures", "CS401", "CSE", "IV", "2025-26"),
    ]
    for name, code, dept_code, semester, acad_year in courses_data:
        if not Course.query.filter_by(code=code).first():
            c = Course(
                name=name, code=code,
                department_id=depts[dept_code].id,
                semester=semester, academic_year=acad_year
            )
            db.session.add(c)

    db.session.commit()
    print("\n[OK] Demo data seeded successfully!")
    print(f"   Departments : {Department.query.count()}")
    print(f"   Faculty     : {Faculty.query.count()}")
    print(f"   Courses     : {Course.query.count()}")
    print("\nAdmin login: username='admin'  password='admin123'")
    print("Visit: http://127.0.0.1:5000\n")
