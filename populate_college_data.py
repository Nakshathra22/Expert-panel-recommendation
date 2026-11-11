"""
populate_college_data.py
========================
Builds the SQLite database populated with real faculty and department data
from Kongu Engineering College for 4 departments:
  1. Computer Science and Design (CSD)
  2. Mechanical Engineering (MECH)
  3. Civil Engineering (CIVIL)
  4. Electrical and Electronics Engineering (EEE)

Usage:
  python populate_college_data.py
"""

import os
import shutil
from app import create_app
from models import db, Admin, Department, Faculty, Course, PanelRequest, ExpertPanel, PanelMember, ActivityLog

app = create_app()

DEPARTMENTS_DATA = [
    {
        "name": "Computer Science and Design",
        "short_code": "CSD",
        "faculty": [
            {
                "name": "Dr. E. Gothai",
                "designation": "Professor & Head of Department",
                "years_of_experience": 19,
                "area_of_expertise": "Big data analytics, Data mining, Deep Learning",
                "email": "egothai@kongu.ac.in",
            },
            {
                "name": "Dr. R. Thangarajan",
                "designation": "Senior Professor",
                "years_of_experience": 28,
                "area_of_expertise": "Theoretical Computer Science, Artificial Intelligence, Natural Language Processing, Machine Learning",
                "email": "thangs_68@kongu.ac.in",
            },
            {
                "name": "Dr. P. Jayanthi",
                "designation": "Professor",
                "years_of_experience": 29,
                "area_of_expertise": "Machine Learning, Deep Learning, Big Data Analytics, Artificial Intelligence",
                "email": "jayanthime@kongu.ac.in",
            },
            {
                "name": "Dr. P. A. Selvaraj",
                "designation": "Associate Professor",
                "years_of_experience": 24,
                "area_of_expertise": "Software testing, Mobile Computing, Cloud Computing, Oops, Web technology, Social Media Networks Analysis, Network Security",
                "email": "kpsraj2001@kongu.ac.in",
            },
            {
                "name": "Dr. K. R. PrasannaKumar",
                "designation": "Associate Professor",
                "years_of_experience": 14,
                "area_of_expertise": "Grid and Cloud computing, Web technology, Android, Data Structures",
                "email": "krprasanna@kongu.ac.in",
            },
            {
                "name": "Dr. S. Anitha",
                "designation": "Associate Professor",
                "years_of_experience": 15,
                "area_of_expertise": "Computer Graphics and multimedia, Wireless Sensor Networks, Network Security, Digital Communication systems, Information Coding Techniques",
                "email": "anithame@kongu.ac.in",
            },
            {
                "name": "Ms. K. Jothimani",
                "designation": "Assistant Professor",
                "years_of_experience": 10,
                "area_of_expertise": "Database Management Systems, Machine Learning",
                "email": "jothimani.csd@kongu.ac.in",
            },
            {
                "name": "Mr. S. Selvaraj",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 14,
                "area_of_expertise": "Computer Networks, HCI, UI/UX, Design thinking, IoT",
                "email": "selvarajs@kongu.ac.in",
            },
            {
                "name": "Mr. T. Velmurugan",
                "designation": "Assistant Professor",
                "years_of_experience": 15,
                "area_of_expertise": "Digital Signal Processing, VLSI Design",
                "email": "velmurugan.csd@kongu.ac.in",
            },
            {
                "name": "Mr. S. B. Gopal",
                "designation": "Associate Professor",
                "years_of_experience": 15,
                "area_of_expertise": "Computer Networks, Network Security",
                "email": "gopal.ece@kongu.ac.in",
            },
            {
                "name": "Ms. S. Hemalatha",
                "designation": "Assistant Professor",
                "years_of_experience": 9,
                "area_of_expertise": "Machine Learning, Deep Learning, Cloud Computing, Data Structure, User Interface Design",
                "email": "hemalatha.csd@kongu.edu",
            },
            {
                "name": "Ms. M. Meenalochini",
                "designation": "Assistant Professor",
                "years_of_experience": 10,
                "area_of_expertise": "Deeplearning, Cyber security, UID/UXD",
                "email": "meenalochini.csd@kongu.ac.in",
            },
            {
                "name": "Ms. A. Deepa",
                "designation": "Assistant Professor",
                "years_of_experience": 5,
                "area_of_expertise": "Cloud computing, Machine learning",
                "email": "deepa.csd@kongu.ac.in",
            },
            {
                "name": "Ms. P. Ananthi",
                "designation": "Assistant Professor",
                "years_of_experience": 3,
                "area_of_expertise": "Data Science, Machine Learning, Programming",
                "email": "ananthi.csd@kongu.ac.in",
            },
            {
                "name": "Ms. K. Vijaya",
                "designation": "Assistant Professor",
                "years_of_experience": 18,
                "area_of_expertise": "WIRELESS NETWORKS, MACHINE LEARNING, NETWORK SECURITY",
                "email": "vijaya.csd@kongu.ac.in",
            },
            {
                "name": "Mr. D. Yuvaraj",
                "designation": "Assistant Professor",
                "years_of_experience": 14,
                "area_of_expertise": "Machine Learning, Deep Learning, Operating systems, image processing",
                "email": "yuvaraj.csd@kongu.ac.in",
            },
            {
                "name": "Ms. R. Yazhini",
                "designation": "Assistant Professor",
                "years_of_experience": 4,
                "area_of_expertise": "Machine Learning, AI concepts and techniques",
                "email": "yazhini.csd@kongu.ac.in",
            },
            {
                "name": "Ms. K. Swathi",
                "designation": "Assistant Professor",
                "years_of_experience": 2,
                "area_of_expertise": "Machine Learning, Deep Learning, UID/UXD",
                "email": "swathi.csd@kongu.edu",
            },
            {
                "name": "Ms. N. Dharshini",
                "designation": "Assistant Professor",
                "years_of_experience": 3,
                "area_of_expertise": "Computer Networks",
                "email": "dharshini.csd@kongu.ac.in",
            },
            {
                "name": "Mr. P. Loganathan",
                "designation": "Assistant Professor",
                "years_of_experience": 14,
                "area_of_expertise": "Wireless Networks, Internet of Things",
                "email": "loganathan.csd@kongu.ac.in",
            },
            {
                "name": "Ms. R. Dharani",
                "designation": "Assistant Professor",
                "years_of_experience": 7,
                "area_of_expertise": "Large Language Models and Generative AI",
                "email": "dharani.csd@kongu.edu",
            },
            {
                "name": "Ms. D. Kabila",
                "designation": "Assistant Professor",
                "years_of_experience": 2,
                "area_of_expertise": "UI/UX Design, Web Development Technologies And Database Management Systems",
                "email": "kabila.csd@kongu.edu",
            },
        ],
        "courses": [
            {"code": "22CSD501", "name": "Deep Learning & Generative AI", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22CSD502", "name": "UI/UX Design & HCI", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22CSD601", "name": "Big Data Analytics & Cloud Computing", "semester": "Semester 6", "year": "2025-2026"},
            {"code": "22CSD602", "name": "Mobile Computing & Network Security", "semester": "Semester 6", "year": "2025-2026"},
        ]
    },
    {
        "name": "Mechanical Engineering",
        "short_code": "MECH",
        "faculty": [
            {
                "name": "Dr. R. Rajasekar",
                "designation": "Senior Professor & Dean & Director",
                "years_of_experience": 15,
                "area_of_expertise": "Material Science and Engineering, Polymer Composites",
                "email": "rajamech@kongu.ac.in",
            },
            {
                "name": "Dr. P. Selvakumar",
                "designation": "Professor & Head of Department",
                "years_of_experience": 19,
                "area_of_expertise": "Solar Energy, Heat Transfer, CFD, Biomaterials",
                "email": "selvakumar@kongu.ac.in",
            },
            {
                "name": "Dr. T. P. Sathishkumar",
                "designation": "Senior Associate Professor",
                "years_of_experience": 18,
                "area_of_expertise": "Fiber reinforced Polymer matrix composites",
                "email": "tpsathish@kongu.ac.in",
            },
            {
                "name": "Dr. A. Mohan Kumar",
                "designation": "Senior Associate Professor",
                "years_of_experience": 15,
                "area_of_expertise": "Composite Materials, CAD",
                "email": "mohankumar@kongu.ac.in",
            },
            {
                "name": "Dr. R. Naveen Kumar",
                "designation": "Senior Associate Professor",
                "years_of_experience": 14,
                "area_of_expertise": "CAD/CAM, Ergonomics",
                "email": "naveenmech@kongu.ac.in",
            },
            {
                "name": "Dr. A. Tamilvanan",
                "designation": "Associate Professor",
                "years_of_experience": 14,
                "area_of_expertise": "Thermal Engineering, Heat Transfer",
                "email": "tamilmech@kongu.ac.in",
            },
            {
                "name": "Dr. M. Bhuvanesh Kumar",
                "designation": "Associate Professor",
                "years_of_experience": 20,
                "area_of_expertise": "Manufacturing Engineering, Industrial Engineering",
                "email": "bhuvanesh@kongu.ac.in",
            },
            {
                "name": "Dr. R. Gukendran",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 17,
                "area_of_expertise": "Production Engineering, Kinematics of Engineering, Dynamics of Machines, Product Data Management, NDT",
                "email": "gukendran@kongu.ac.in",
            },
            {
                "name": "Dr. M. Sambathkumar",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 17,
                "area_of_expertise": "Fluid Power System, Theory of Machines, Metal Matrix Composites, Engineering Drawing, Design of Transmission System",
                "email": "sambathkumar@kongu.ac.in",
            },
            {
                "name": "Dr. B. S. Hari",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 14,
                "area_of_expertise": "CAD/CAM, Finite Element Analysis",
                "email": "harimech@kongu.ac.in",
            },
            {
                "name": "Dr. M. Mahesh",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 11,
                "area_of_expertise": "Energy Engineering, Thermal Sciences",
                "email": "mmahesh.mech@kongu.ac.in",
            },
            {
                "name": "Mr. K. V. Satheesh Kumar",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 19,
                "area_of_expertise": "Welding, Optimization Techniques",
                "email": "kvs@kongu.ac.in",
            },
            {
                "name": "Mr. R. Karthikeyan",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 11,
                "area_of_expertise": "Thermal Engineering, Renewable Energy",
                "email": "karthi.mech@kongu.ac.in",
            },
            {
                "name": "Mr. M. Dharmaraj",
                "designation": "Assistant Professor (SRG)",
                "years_of_experience": 26,
                "area_of_expertise": "Engineering Design, Machine Elements",
                "email": "mdmech@kongu.ac.in",
            },
            {
                "name": "Mr. R. Kamalakannan",
                "designation": "Assistant Professor (SRG)",
                "years_of_experience": 15,
                "area_of_expertise": "Advanced Manufacturing, Machining Processes",
                "email": "kamalakannan.mech@kongu.ac.in",
            },
            {
                "name": "Mr. A. Ganesh",
                "designation": "Assistant Professor (SRG)",
                "years_of_experience": 10,
                "area_of_expertise": "Thermal Engineering, Solar Distillation, Renewable Energy Sources",
                "email": "ganesh@kongu.ac.in",
            },
        ],
        "courses": [
            {"code": "22MEC501", "name": "Thermal Engineering & Heat Transfer", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22MEC502", "name": "CAD/CAM & Industrial Automation", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22MEC601", "name": "Composite Materials & Mechanics", "semester": "Semester 6", "year": "2025-2026"},
            {"code": "22MEC602", "name": "Design of Transmission Systems", "semester": "Semester 6", "year": "2025-2026"},
        ]
    },
    {
        "name": "Civil Engineering",
        "short_code": "CIVIL",
        "faculty": [
            {
                "name": "Dr. S. Balaji",
                "designation": "Professor & Head of Department",
                "years_of_experience": 20,
                "area_of_expertise": "Structural Engineering, Concrete Structures",
                "email": "balaji.civil@kongu.ac.in",
            },
            {
                "name": "Dr. G. S. Rampradheep",
                "designation": "Senior Associate Professor",
                "years_of_experience": 15,
                "area_of_expertise": "Structural Engineering, Concrete Technology",
                "email": "rampradheep@kongu.ac.in",
            },
            {
                "name": "Dr. T. Pradeep",
                "designation": "Associate Professor",
                "years_of_experience": 17,
                "area_of_expertise": "Environmental Engineering, Water Resources Engineering",
                "email": "pradeep@kongu.ac.in",
            },
            {
                "name": "Dr. S. Karthikeyan",
                "designation": "Associate Professor",
                "years_of_experience": 17,
                "area_of_expertise": "Fibre Reinforced Concrete, Structural Analysis & Design of Steel Structures",
                "email": "karthikeyan.civil@kongu.ac.in",
            },
            {
                "name": "Dr. V. Sampathkumar",
                "designation": "Associate Professor",
                "years_of_experience": 13,
                "area_of_expertise": "Environmental Engineering, Pollution Control",
                "email": "sampath.civil@kongu.ac.in",
            },
            {
                "name": "Dr. K. Vishnuvardhan",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 16,
                "area_of_expertise": "Transportation Engineering, Highway Design",
                "email": "vishnukaruna@kongu.ac.in",
            },
            {
                "name": "Dr. K. S. Navaneethan",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 11,
                "area_of_expertise": "Structural Members, Retrofitting & Concrete Technology, Structural Engineering",
                "email": "navaneethanks.civil@kongu.ac.in",
            },
            {
                "name": "Dr. S. Manoj",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 12,
                "area_of_expertise": "Water Resource Engineering, Water and Land Management",
                "email": "manoj.civil@kongu.ac.in",
            },
            {
                "name": "Mr. S. Venkatachalam",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 13,
                "area_of_expertise": "Concrete Composite, Ergonomics, Geo-Polymer Concrete",
                "email": "venkatcivil@kongu.ac.in",
            },
            {
                "name": "Mr. T. Ravi Prakash",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 13,
                "area_of_expertise": "Textile Reinforced Concrete, Structural Engineering",
                "email": "ktravi@kongu.ac.in",
            },
            {
                "name": "Mr. K. Sampath Kumar",
                "designation": "Assistant Professor (SLG)",
                "years_of_experience": 6,
                "area_of_expertise": "Concrete Technology, Construction Engineering & Management",
                "email": "sampathkumar.civil@kongu.ac.in",
            },
        ],
        "courses": [
            {"code": "22CIV501", "name": "Design of Reinforced Concrete Structures", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22CIV502", "name": "Environmental Engineering & Water Resources", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22CIV601", "name": "Transportation & Highway Engineering", "semester": "Semester 6", "year": "2025-2026"},
            {"code": "22CIV602", "name": "Structural Analysis & Steel Design", "semester": "Semester 6", "year": "2025-2026"},
        ]
    },
    {
        "name": "Electrical and Electronics Engineering",
        "short_code": "EEE",
        "faculty": [
            {
                "name": "Dr. M. Karthik",
                "designation": "Professor & Head of Department",
                "years_of_experience": 22,
                "area_of_expertise": "Hybrid Electric Vehicle and Fuel Cell applications",
                "email": "karthik.eee@kongu.ac.in",
            },
            {
                "name": "Dr. N. Senthilnathan",
                "designation": "Professor",
                "years_of_experience": 24,
                "area_of_expertise": "Power Quality, High Voltage Systems",
                "email": "senthilnathan.eee@kongu.ac.in",
            },
            {
                "name": "Dr. M. Sivachitra",
                "designation": "Professor",
                "years_of_experience": 26,
                "area_of_expertise": "Soft computing, Signal Processing",
                "email": "sivachitra.eee@kongu.ac.in",
            },
            {
                "name": "Dr. S. Usha",
                "designation": "Associate Professor",
                "years_of_experience": 17,
                "area_of_expertise": "Image Processing, Pattern Recognition",
                "email": "usha.eee@kongu.ac.in",
            },
            {
                "name": "Dr. S. Maheswari",
                "designation": "Associate Professor",
                "years_of_experience": 16,
                "area_of_expertise": "Signal and Image Processing",
                "email": "maheswari.eee@kongu.ac.in",
            },
            {
                "name": "Dr. T. Logeswaran",
                "designation": "Associate Professor",
                "years_of_experience": 18,
                "area_of_expertise": "Renewable Energy, Power Quality",
                "email": "logeswaran.eee@kongu.ac.in",
            },
            {
                "name": "Dr. T. Gunasekar",
                "designation": "Associate Professor",
                "years_of_experience": 16,
                "area_of_expertise": "Power System, Power Quality",
                "email": "gunasekar.eee@kongu.ac.in",
            },
            {
                "name": "Dr. V. Surendar",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 15,
                "area_of_expertise": "Power Electronics for Renewable Energy Sources",
                "email": "surendar.eee@kongu.ac.in",
            },
            {
                "name": "Dr. M. Suresh",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 14,
                "area_of_expertise": "Nature Inspired Algorithms, Power Systems",
                "email": "suresh.eee@kongu.ac.in",
            },
            {
                "name": "Dr. N. Priyadharshini",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 14,
                "area_of_expertise": "Power System (State Estimation PMU locations)",
                "email": "priyadharshini.eee@kongu.ac.in",
            },
            {
                "name": "Dr. S. Gomathy",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 14,
                "area_of_expertise": "DC to DC Converters, Power Electronics",
                "email": "gomathy.eee@kongu.ac.in",
            },
            {
                "name": "Dr. M. Sabarimuthu",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 14,
                "area_of_expertise": "Electric Vehicles & Fast Chargers",
                "email": "sabarimuthu.eee@kongu.ac.in",
            },
            {
                "name": "Dr. M. Srinivasan",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 13,
                "area_of_expertise": "High Voltage Engineering",
                "email": "srinivasan.eee@kongu.ac.in",
            },
            {
                "name": "Dr. P. Tamilarasu",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 13,
                "area_of_expertise": "Power System, Power Quality",
                "email": "tamilarasu.eee@kongu.ac.in",
            },
            {
                "name": "Dr. M. Suresh (HV)",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 11,
                "area_of_expertise": "High Voltage Engineering, Power System",
                "email": "msuresh.eee@kongu.ac.in",
            },
            {
                "name": "Dr. D. Sarathkumar",
                "designation": "Assistant Professor (Selection Grade)",
                "years_of_experience": 11,
                "area_of_expertise": "Micro Grid, Liquid Dielectrics",
                "email": "sarathkumar.eee@kongu.ac.in",
            },
            {
                "name": "Mr. S. Chandrasekar",
                "designation": "Assistant Professor (Senior Grade)",
                "years_of_experience": 16,
                "area_of_expertise": "Applied Electronics, EV and Charge Controllers",
                "email": "chandrasekar.eee@kongu.ac.in",
            },
            {
                "name": "Mr. P. Karthikeyan",
                "designation": "Assistant Professor (Senior Grade)",
                "years_of_experience": 15,
                "area_of_expertise": "DC to DC converters, Power Electronics",
                "email": "pkarthikeyan.eee@kongu.ac.in",
            },
            {
                "name": "Mr. R. Ranjith Kumar",
                "designation": "Assistant Professor (Senior Grade)",
                "years_of_experience": 13,
                "area_of_expertise": "Distribution System, Smart Grid",
                "email": "ranjithkumar.eee@kongu.ac.in",
            },
            {
                "name": "Mr. B. Ravisankar",
                "designation": "Assistant Professor (Senior Grade)",
                "years_of_experience": 1,
                "area_of_expertise": "Electrical Drives and Embedded Control",
                "email": "ravisankar.eee@kongu.ac.in",
            },
            {
                "name": "Ms. V. Pavithra",
                "designation": "Assistant Professor",
                "years_of_experience": 1,
                "area_of_expertise": "Power Electronics and Drives",
                "email": "pavithra.eee@kongu.ac.in",
            },
            {
                "name": "Mr. R. Aravindh",
                "designation": "Assistant Professor",
                "years_of_experience": 1,
                "area_of_expertise": "Power Electronics and Drives",
                "email": "aravindh.eee@kongu.ac.in",
            },
            {
                "name": "Mr. M. Venkatachalam",
                "designation": "Assistant Professor",
                "years_of_experience": 1,
                "area_of_expertise": "Power Electronics and Drives",
                "email": "venkatachalam.eee@kongu.ac.in",
            },
            {
                "name": "Mr. D. Thangaraj",
                "designation": "Assistant Professor",
                "years_of_experience": 1,
                "area_of_expertise": "Electrical Vehicle, Automotive Electronics",
                "email": "thangaraj.eee@kongu.ac.in",
            },
        ],
        "courses": [
            {"code": "22EEE501", "name": "Power Electronics & Solid State Drives", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22EEE502", "name": "Hybrid Electric Vehicles & Energy Storage", "semester": "Semester 5", "year": "2025-2026"},
            {"code": "22EEE601", "name": "Micro Grid Architecture & Smart Grid", "semester": "Semester 6", "year": "2025-2026"},
            {"code": "22EEE602", "name": "Renewable Energy & Power Quality Analysis", "semester": "Semester 6", "year": "2025-2026"},
        ]
    }
]


def populate():
    with app.app_context():
        # Clear existing tables cleanly
        PanelMember.query.delete()
        ExpertPanel.query.delete()
        PanelRequest.query.delete()
        Course.query.delete()
        Faculty.query.delete()
        Department.query.delete()
        ActivityLog.query.delete()
        Admin.query.delete()
        db.session.commit()

        # 1. Admin account
        admin = Admin(
            username=app.config["ADMIN_USERNAME"],
            email="admin@kongu.ac.in"
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(f"[*] Admin user ready: username='{admin.username}', password='{app.config['ADMIN_PASSWORD']}'")

        # 2. Departments, Faculty, and Courses
        total_faculty = 0
        total_courses = 0

        for dept_info in DEPARTMENTS_DATA:
            dept = Department(
                name=dept_info["name"],
                short_code=dept_info["short_code"]
            )
            db.session.add(dept)
            db.session.flush()

            # Add Faculty
            for f_info in dept_info["faculty"]:
                f = Faculty(
                    name=f_info["name"],
                    email=f_info["email"].lower().strip(),
                    designation=f_info["designation"],
                    years_of_experience=f_info["years_of_experience"],
                    area_of_expertise=f_info["area_of_expertise"],
                    department_id=dept.id,
                    is_active=True
                )
                db.session.add(f)
                total_faculty += 1

            # Add Courses
            for c_info in dept_info["courses"]:
                c = Course(
                    name=c_info["name"],
                    code=c_info["code"],
                    semester=c_info["semester"],
                    academic_year=c_info["year"],
                    department_id=dept.id,
                    status="pending"
                )
                db.session.add(c)
                total_courses += 1

        db.session.commit()
        print(f"[+] Successfully loaded {len(DEPARTMENTS_DATA)} departments:")
        for d in Department.query.all():
            print(f"    - {d.name} ({d.short_code}) | Faculty: {d.faculty.count()} | Courses: {d.courses.count()}")

        print(f"[+] Total Faculty inserted: {total_faculty}")
        print(f"[+] Total Courses inserted: {total_courses}")

        # Also copy a standalone export of the SQLite database
        db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, db_path)

        standalone_export = os.path.join(app.root_path, "kongu_expert_panel.db")
        if os.path.exists(db_path):
            shutil.copy2(db_path, standalone_export)
            print(f"[+] Standalone database export created at: {standalone_export}")


if __name__ == "__main__":
    populate()
