import os
import shutil
import sqlite3
from app import create_app
from models import db, Department, Faculty, Course

app = create_app()

NEW_DATA = [
    {
        "name": "Computer Science and Engineering",
        "short_code": "CSE",
        "courses": [
            {"code": "22CSC501", "name": "Design and Analysis of Algorithms", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22CSC502", "name": "Computer Networks & Security", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22CSC601", "name": "Artificial Intelligence & Machine Learning", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22CSC602", "name": "Cloud Computing and Big Data", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. S. Malliga", "designation": "Senior Professor & Head", "years_of_experience": 25, "area_of_expertise": "Computer Networks, Network Security, Wireless Sensor Network, IoT", "email": "malliga@kongu.ac.in"},
            {"name": "Dr. C. S. Kanimozhiselvi", "designation": "Professor", "years_of_experience": 25, "area_of_expertise": "Machine Learning, Data Science, Natural Language Processing", "email": "kanimozhiselvi@kongu.ac.in"},
            {"name": "Dr. N. Shanthi", "designation": "Professor", "years_of_experience": 25, "area_of_expertise": "Image Processing, Machine Learning and Network Security", "email": "shanthi.cse@kongu.ac.in"},
            {"name": "Dr. R. Thamilselvan", "designation": "Professor", "years_of_experience": 25, "area_of_expertise": "Cloud and Grid Computing, BigData, Nature Inspired Algorithms", "email": "thamilselvan@kongu.ac.in"},
            {"name": "Dr. E. Gothai", "designation": "Professor", "years_of_experience": 25, "area_of_expertise": "Big Data Analytics, Data Mining, Deep Learning", "email": "gothai.cse@kongu.ac.in"},
            {"name": "Dr. K. Sangeetha", "designation": "Professor", "years_of_experience": 20, "area_of_expertise": "Computer Networks, Adhoc Network, IoT", "email": "sangeetha.cse@kongu.ac.in"},
            {"name": "Dr. S. Shanthi", "designation": "Professor", "years_of_experience": 26, "area_of_expertise": "Data Mining, Image Processing, Artificial Intelligence", "email": "sshanthi.cse@kongu.ac.in"},
            {"name": "Dr. K. Nirmala Devi", "designation": "Associate Professor", "years_of_experience": 28, "area_of_expertise": "Data Mining, Big Data Analytics, Machine Learning", "email": "nirmaladevi.cse@kongu.ac.in"},
            {"name": "Dr. P. C. D. Kalaivaani", "designation": "Associate Professor", "years_of_experience": 25, "area_of_expertise": "Data Mining, Web Mining, Sentiment Analysis", "email": "kalaivaani.cse@kongu.ac.in"},
            {"name": "Dr. M. Geetha", "designation": "Associate Professor", "years_of_experience": 19, "area_of_expertise": "Cloud Computing, Multimedia, Nature Inspired Optimization Algorithms, Machine Learning", "email": "geetha.cse@kongu.ac.in"},
            {"name": "Dr. N. Sasipriyaa", "designation": "Associate Professor", "years_of_experience": 19, "area_of_expertise": "Data Mining, Deep Learning, Image Processing", "email": "sasipriyaa.cse@kongu.ac.in"},
            {"name": "Dr. K. Dinesh", "designation": "Associate Professor", "years_of_experience": 10, "area_of_expertise": "Cloud Computing, Distributed Systems, Network Security", "email": "dinesh.cse@kongu.ac.in"},
            {"name": "Dr. P. S. Nandhini", "designation": "Associate Professor", "years_of_experience": 12, "area_of_expertise": "Deep Learning, Computer Networks, Internet of Things, Network Security", "email": "nandhini.cse@kongu.ac.in"},
            {"name": "Mr. N. P. Saravanan", "designation": "Assistant Professor", "years_of_experience": 25, "area_of_expertise": "Distributed Computing, Cloud Computing, Operating Systems", "email": "saravanan.cse@kongu.ac.in"},
            {"name": "Mr. T. Kumaravel", "designation": "Assistant Professor", "years_of_experience": 15, "area_of_expertise": "Deep Learning, Machine Learning, Data Analytics", "email": "kumaravel.cse@kongu.ac.in"},
            {"name": "Ms. S. Ramya", "designation": "Assistant Professor", "years_of_experience": 16, "area_of_expertise": "Data Base Management Systems, Big Data, Cloud Computing", "email": "ramya.cse@kongu.ac.in"},
            {"name": "Mr. K. Devendran", "designation": "Assistant Professor", "years_of_experience": 16, "area_of_expertise": "Data Mining, Web Technology, Android Application Development", "email": "devendran.cse@kongu.ac.in"},
            {"name": "Mr. B. Bizu", "designation": "Assistant Professor", "years_of_experience": 15, "area_of_expertise": "Machine Learning, Deep Learning, Artificial Intelligence", "email": "bizu.cse@kongu.ac.in"},
            {"name": "Ms. C. Sagana", "designation": "Assistant Professor", "years_of_experience": 13, "area_of_expertise": "Cloud Computing, Machine Learning, Deep Learning", "email": "sagana.cse@kongu.ac.in"},
            {"name": "Dr. B. Krishnakumar", "designation": "Assistant Professor", "years_of_experience": 18, "area_of_expertise": "Cloud Computing, Machine Learning, Software Engineering", "email": "krishnakumar.cse@kongu.ac.in"},
            {"name": "Ms. S. Mohana Saranya", "designation": "Assistant Professor", "years_of_experience": 12, "area_of_expertise": "Deep Learning, Big Data Analytics, Neural Networks", "email": "mohanasaranya.cse@kongu.ac.in"},
            {"name": "Ms. S. Mohanapriya", "designation": "Assistant Professor", "years_of_experience": 12, "area_of_expertise": "Machine Learning Algorithms, Computer Vision, Deep Learning", "email": "mohanapriya.cse@kongu.ac.in"},
            {"name": "Ms. K. Venu", "designation": "Assistant Professor", "years_of_experience": 10, "area_of_expertise": "Block chain Technology, Cryptography, Data Security", "email": "venu.cse@kongu.ac.in"},
            {"name": "Ms. J. Gowthami", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Natural Language Processing, Machine Learning, Cloud Computing", "email": "gowthami.cse@kongu.ac.in"},
            {"name": "Ms. T. E. Ramya", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Machine Learning, Deep Learning, Image Processing", "email": "teramya.cse@kongu.ac.in"},
            {"name": "Ms. S. Gayathri", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Natural Language Processing, Machine Learning, Cloud Computing", "email": "gayathri.cse@kongu.ac.in"},
            {"name": "Ms. R. S. Shudapreya", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Machine Learning, Deep Learning, Data Analytics", "email": "shudapreya.cse@kongu.ac.in"},
            {"name": "Ms. S. Kavitha", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Machine Learning, Deep Learning, Data Mining, Image Processing", "email": "kavitha.cse@kongu.ac.in"},
            {"name": "Mr. M. Muthuraja", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Machine Learning, Deep Learning, Computer Networks", "email": "muthuraja.cse@kongu.ac.in"},
            {"name": "Ms. P. Santhiya", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Computer Networks, Machine Learning, Deep Learning", "email": "santhiya.cse@kongu.ac.in"},
            {"name": "Mr. V. Manimaran", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Data Structure, Network Security, Cloud Computing, Database Management System", "email": "manimaran.cse@kongu.ac.in"},
            {"name": "Ms. P. Kalaivani", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Data Science, Machine Learning, Big Data", "email": "kalaivani.cse@kongu.ac.in"},
            {"name": "Ms. C. Roopa", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Artificial Intelligence", "email": "roopa.cse@kongu.ac.in"},
            {"name": "Ms. K. Suvalakshmi", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Computer Vision", "email": "suvalakshmi.cse@kongu.ac.in"},
            {"name": "Mr. K. Sureshkumar", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Computer Networks, Machine Learning, Internet of Things", "email": "sureshkumar.cse@kongu.ac.in"},
            {"name": "Mr. T. Arunkumar", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Machine Learning, Deep Learning, Data Structures", "email": "arunkumar.cse@kongu.ac.in"},
            {"name": "Dr. T. Nagamani", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Artificial Intelligence, Data Science, Machine Learning", "email": "nagamani.cse@kongu.ac.in"},
            {"name": "Ms. M. Kannukkiniyal", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Software Engineering, Web Technologies, Cloud Services", "email": "kannukkiniyal.cse@kongu.ac.in"},
            {"name": "Mr. N. Aravindhraj", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Software Engineering and Deep Learning, Full Stack", "email": "aravindhraj.cse@kongu.ac.in"},
            {"name": "Ms. K. T. Mohanapriya", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Edge Computing, Internet of Things, C and Java", "email": "ktmohanapriya.cse@kongu.ac.in"},
            {"name": "Ms. S. Ramana", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Programming Design, Algorithms, Python", "email": "ramana.cse@kongu.ac.in"},
            {"name": "Ms. S. Kalpana", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Digital Electronics, VLSI Design, Hardware Description Languages", "email": "kalpana.cse@kongu.ac.in"},
            {"name": "Ms. P. Jeevitha", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Low Power VLSI, Digital Systems, Microcontrollers", "email": "jeevitha.cse@kongu.ac.in"},
            {"name": "Ms. P. Yuvarani", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Electronics and VLSI Design, Embedded Systems", "email": "yuvarani.cse@kongu.ac.in"},
            {"name": "Ms. T. Sathya", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Signal Processing, VLSI, Instrumentation", "email": "tsathya.cse@kongu.ac.in"},
            {"name": "Mr. K. Sudhakar", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "VLSI Design, Signal Processing, Digital Logic", "email": "sudhakar.cse@kongu.ac.in"},
            {"name": "Ms. T. Vanaja", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Programming in Python and MIMO systems, Wireless Communications", "email": "vanaja.cse@kongu.ac.in"},
            {"name": "Ms. A. Kiruthika", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Deep Learning, Data Structures", "email": "kiruthika.cse@kongu.ac.in"},
            {"name": "Ms. S. Madhumitha", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Data Science and Artificial Intelligence, Python", "email": "madhumitha.cse@kongu.ac.in"},
            {"name": "Ms. M. Kowsalya", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Data Structure and Algorithms, Machine Learning", "email": "kowsalya.cse@kongu.ac.in"},
            {"name": "Ms. S. Karthika", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Data Structure and Algorithms, Machine Learning, Digital Electronics, VLSI Design", "email": "karthika.cse@kongu.ac.in"}
        ]
    },
    {
        "name": "Information Technology",
        "short_code": "IT",
        "courses": [
            {"code": "22ITT501", "name": "Wireless Sensor Networks & IoT", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22ITT502", "name": "Cryptography & Network Security", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22ITT601", "name": "Cloud Computing and Distributed Systems", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22ITT602", "name": "Full Stack Web Development & Mobile Apps", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. S. Anandamurugan", "designation": "Professor", "years_of_experience": 23, "area_of_expertise": "Wireless Sensor Networks, IoT, Mobile Computing", "email": "anandamurugan.it@kongu.ac.in"},
            {"name": "Dr. S. Varadhaganapathy", "designation": "Senior Professor & Head", "years_of_experience": 35, "area_of_expertise": "Ad Hoc Networks, Network Security, Programming Languages", "email": "varadhaganapathy@kongu.ac.in"},
            {"name": "Dr. J. Premalatha", "designation": "Professor", "years_of_experience": 24, "area_of_expertise": "Cryptography & Network Security, Computer Networks, Database Management System", "email": "premalatha.it@kongu.ac.in"},
            {"name": "Dr. T. Abirami", "designation": "Associate Professor", "years_of_experience": 23, "area_of_expertise": "Wireless Sensor Networks, Computer Networks, Soft Computing Techniques", "email": "abirami.it@kongu.ac.in"},
            {"name": "Dr. G. K. Kamalam", "designation": "Associate Professor", "years_of_experience": 26, "area_of_expertise": "Grid and Cloud Computing, Optimization Techniques, Data Structure and Algorithm Analysis", "email": "kamalam.it@kongu.ac.in"},
            {"name": "Dr. R. Shanthakumari", "designation": "Associate Professor", "years_of_experience": 26, "area_of_expertise": "Network Security and Image Processing, Computer Vision", "email": "shanthakumari.it@kongu.ac.in"},
            {"name": "Dr. E. M. Roopa Devi", "designation": "Associate Professor", "years_of_experience": 20, "area_of_expertise": "Network Security, Data Mining, Information Assurance", "email": "roopadevi.it@kongu.ac.in"},
            {"name": "Mr. D. Vijay Anand", "designation": "Assistant Professor (SLG)", "years_of_experience": 15, "area_of_expertise": "Data Mining, Big Data Analytics, Machine Learning", "email": "vijayanand.it@kongu.ac.in"},
            {"name": "Mr. S. Vinothkumar", "designation": "Assistant Professor (SRG)", "years_of_experience": 14, "area_of_expertise": "Network Security, Communication Engineering, Digital Electronics", "email": "vinothkumar.it@kongu.ac.in"},
            {"name": "Mr. A. P. Ponselvakumar", "designation": "Assistant Professor (SRG)", "years_of_experience": 17, "area_of_expertise": "Information Retrieval, Web Mining, Natural Language Processing", "email": "ponselvakumar.it@kongu.ac.in"},
            {"name": "Mr. A. Jeevanantham", "designation": "Assistant Professor (SRG)", "years_of_experience": 12, "area_of_expertise": "Internet of Things, Network Security, Cyber Physical Systems", "email": "jeevanantham.it@kongu.ac.in"},
            {"name": "Dr. V. Devisurya", "designation": "Assistant Professor (SRG)", "years_of_experience": 5, "area_of_expertise": "Programming Languages, Data Structures, Algorithms", "email": "devisurya.it@kongu.ac.in"},
            {"name": "Ms. S. Sujitha", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Cloud Computing, Machine Learning, Deep Learning", "email": "sujitha.it@kongu.ac.in"},
            {"name": "Ms. R. Aarthi", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Computer Networks, Database Management Systems", "email": "aarthi.it@kongu.ac.in"},
            {"name": "Ms. K. Sruthi", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Datastructures, Database, Machine Learning", "email": "sruthi.it@kongu.ac.in"},
            {"name": "Ms. S. Kavithra", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "DBMS, Programming, Machine Learning, C Programming", "email": "kavithra.it@kongu.ac.in"},
            {"name": "Ms. R. Sandhiya", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "DBMS, C Programming, Machine Learning", "email": "sandhiya.it@kongu.ac.in"},
            {"name": "Ms. V. P. Gayathri", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Computer Networks, Data Structures, Web Design", "email": "vpgayathri.it@kongu.ac.in"},
            {"name": "Ms. P. Vanitha", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Python programming, DBMS, Data Analytics", "email": "vanitha.it@kongu.ac.in"},
            {"name": "Ms. A. Deenu Mol", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "C Programming, Python programming, Web Development", "email": "deenumol.it@kongu.ac.in"},
            {"name": "Dr. S. Subashini", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Data Structures, DBMS, Networks", "email": "subashini.it@kongu.ac.in"},
            {"name": "Ms. T. Vaishnavi", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Data Structures, C Programming, Deep Learning", "email": "vaishnavi.it@kongu.ac.in"},
            {"name": "Ms. S. Krishnaveni", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Java, Machine Learning, Web Development", "email": "krishnaveni.it@kongu.ac.in"},
            {"name": "Ms. M. E. Prathika", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Digital Electronics, VLSI, Embedded Systems", "email": "prathika.it@kongu.ac.in"},
            {"name": "Ms. T. S. Vishnu Priya", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Data Analytics, Artificial Intelligence", "email": "vishnupriya.it@kongu.ac.in"},
            {"name": "Ms. Monica Murugesan", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Python Programming, Web Development, Cloud Computing", "email": "monica.it@kongu.ac.in"},
            {"name": "Ms. S. Suganya", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "DBMS, Data structures, Software Engineering", "email": "suganya.it@kongu.ac.in"},
            {"name": "Ms. G. Sasikala", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Data Structures, DBMS, Machine Learning, Theory of Computation", "email": "sasikala.it@kongu.ac.in"},
            {"name": "Ms. E. Sowmiya", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Logic Design, Operating System, Ethical Hacking", "email": "sowmiya.it@kongu.ac.in"},
            {"name": "Ms. S. Sripriya", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Artificial Intelligence, Generative AI, DBMS, Machine Learning", "email": "sripriya.it@kongu.ac.in"},
            {"name": "Mr. N. Nithyakumar", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Digital Logic Design, Information Theory & Coding, Computer Networks", "email": "nithyakumar.it@kongu.ac.in"},
            {"name": "Mr. S. Govindaraj", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Signal Processing, Image Processing, Information Theory and Coding", "email": "govindaraj.it@kongu.ac.in"}
        ]
    },
    {
        "name": "Artificial Intelligence and Data Science",
        "short_code": "AIDS",
        "courses": [
            {"code": "22ADT501", "name": "Foundations of Data Science & Big Data", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22ADT502", "name": "Machine Learning & Pattern Recognition", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22ADT601", "name": "Deep Learning and Neural Architectures", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22ADT602", "name": "Natural Language Processing & Speech Analytics", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. P. Natesan", "designation": "Professor & Head", "years_of_experience": 24, "area_of_expertise": "Computer Network Security, Machine Learning, Data Analytics", "email": "natesan.aids@kongu.ac.in"},
            {"name": "Dr. R. S. Latha", "designation": "Professor", "years_of_experience": 20, "area_of_expertise": "Wireless Networks, Machine Learning, Deep Learning", "email": "rslatha.aids@kongu.ac.in"},
            {"name": "Dr. S. Kayalvili", "designation": "Associate Professor", "years_of_experience": 18, "area_of_expertise": "Cloud Computing, Security, Artificial Intelligence", "email": "kayalvili.aids@kongu.ac.in"},
            {"name": "Dr. K. S. Kalaivani", "designation": "Associate Professor", "years_of_experience": 13, "area_of_expertise": "Machine Learning, Deep Learning, Computer Vision", "email": "kalaivani.aids@kongu.ac.in"},
            {"name": "Dr. M. Vimaladevi", "designation": "Associate Professor", "years_of_experience": 12, "area_of_expertise": "Data Mining, Machine Learning, Big Data Analytics", "email": "vimaladevi.aids@kongu.ac.in"},
            {"name": "Ms. A. S. Renugadevi", "designation": "Assistant Professor", "years_of_experience": 6, "area_of_expertise": "Computer Networks, Machine Learning, Deep Learning", "email": "renugadevi.aids@kongu.ac.in"},
            {"name": "Ms. N. Kanimozhi", "designation": "Assistant Professor", "years_of_experience": 6, "area_of_expertise": "Machine Learning, Deep Learning, Natural Language Processing", "email": "kanimozhi.aids@kongu.ac.in"},
            {"name": "Ms. P. Jayadharshini", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Cloud Computing", "email": "jayadharshini.aids@kongu.ac.in"},
            {"name": "Ms. P. Ramya", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Data Analytics", "email": "ramya.aids@kongu.ac.in"},
            {"name": "Ms. J. Charanya", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Computer Networks, Data Structures", "email": "charanya.aids@kongu.ac.in"},
            {"name": "Ms. S. Keerthika", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Artificial Intelligence", "email": "keerthika.aids@kongu.ac.in"},
            {"name": "Dr. S. Priyanka", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Data Mining", "email": "priyanka.aids@kongu.ac.in"},
            {"name": "Ms. D. Sathya", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Predictive Modeling", "email": "sathya.aids@kongu.ac.in"},
            {"name": "Ms. R. Thangamani", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Machine Learning, Deep Learning, Statistical Analysis", "email": "thangamani.aids@kongu.ac.in"},
            {"name": "Ms. M. Sri Kruthika", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Machine Learning, Deep Learning, Neural Networks", "email": "srikruthika.aids@kongu.ac.in"},
            {"name": "Ms. M. M. Ramyasri", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Machine Learning, Deep Learning, Big Data Analytics", "email": "ramyasri.aids@kongu.ac.in"},
            {"name": "Mr. N. Kannan", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Machine Learning, Deep Learning, Data Visualization", "email": "kannan.aids@kongu.ac.in"},
            {"name": "Ms. M. Harini", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Deep Learning, Python Programming", "email": "harini.aids@kongu.ac.in"},
            {"name": "Dr. T. A. Karthikeyan", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Antennas, Communication Systems, Signal Processing", "email": "karthikeyan.aids@kongu.ac.in"},
            {"name": "Ms. M. Mohana Arasi", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Applied Electronics, Embedded Systems, IoT", "email": "mohanaarasi.aids@kongu.ac.in"},
            {"name": "Mr. N. Vigneshwaran", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Communication Systems, Wireless Networking", "email": "vigneshwaran.aids@kongu.ac.in"},
            {"name": "Ms. S. Gayathri", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Artificial Intelligence, Data Structures", "email": "gayathri.aids@kongu.ac.in"},
            {"name": "Mr. R. Arunkumar", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Automata Theory, Discrete Mathematics", "email": "arunkumar.aids@kongu.ac.in"},
            {"name": "Ms. G. Balashanthi", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Deep Learning, Data Engineering", "email": "balashanthi.aids@kongu.ac.in"},
            {"name": "Ms. S. Shangavi", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Deep Learning, Computer Vision", "email": "shangavi.aids@kongu.ac.in"}
        ]
    },
    {
        "name": "Artificial Intelligence and Machine Learning",
        "short_code": "AIML",
        "courses": [
            {"code": "22AML501", "name": "Supervised & Unsupervised Learning", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22AML502", "name": "Nature Inspired Computing & Optimization", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22AML601", "name": "Deep Reinforcement Learning", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22AML602", "name": "Computer Vision & Generative Models", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. R. R. Rajalaxmi", "designation": "Senior Professor & Head", "years_of_experience": 25, "area_of_expertise": "Data Mining, Nature Inspired Computing, Machine Learning, Deep Learning", "email": "rajalaxmi@kongu.ac.in"},
            {"name": "Dr. C. Nalini", "designation": "Professor", "years_of_experience": 22, "area_of_expertise": "Data Structures, Data Mining, Design and Analysis of Algorithms", "email": "nalini.aiml@kongu.ac.in"},
            {"name": "Dr. K. Logeswaran", "designation": "Associate Professor", "years_of_experience": 15, "area_of_expertise": "Machine Learning, Data Mining, Pattern Recognition", "email": "logeswaran@kongu.ac.in"},
            {"name": "Dr. K. Sathya", "designation": "Associate Professor", "years_of_experience": 10, "area_of_expertise": "Network Security, Blockchain, Java Programming", "email": "sathya.aiml@kongu.ac.in"},
            {"name": "Ms. S. Hamsanandhini", "designation": "Assistant Professor", "years_of_experience": 10, "area_of_expertise": "Cloud Computing, Network Security, Data Mining", "email": "hamsanandhini.aiml@kongu.ac.in"},
            {"name": "Ms. S. Santhiya", "designation": "Assistant Professor", "years_of_experience": 5, "area_of_expertise": "Deep Learning, Machine Learning", "email": "santhiya.aiml@kongu.ac.in"},
            {"name": "Ms. S. Benil Jeniffer", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Machine Learning, Deep Learning, Computer Vision", "email": "beniljeniffer.aiml@kongu.ac.in"},
            {"name": "Ms. K. Senthilvadivu", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Wireless Sensor Networks, Machine Learning", "email": "senthilvadivu.aiml@kongu.ac.in"},
            {"name": "Ms. M. Yoga", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Machine Learning, Deep Learning, Natural Language Processing", "email": "yoga.aiml@kongu.ac.in"},
            {"name": "Ms. O. Abhila Anju", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Machine Learning, Deep Learning, Image Analytics", "email": "abhilaanju.aiml@kongu.ac.in"},
            {"name": "Mr. M. Neelamegan", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Deep Learning, Computer Networks, Neural Networks", "email": "neelamegan.aiml@kongu.ac.in"},
            {"name": "Mr. S. Gopinath", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Wireless Communication Systems, Satellite & RF Communication, Wireless Networks", "email": "gopinath.aiml@kongu.ac.in"},
            {"name": "Ms. N. Renuka", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Machine Learning, Deep Learning, Predictive Analytics", "email": "renuka.aiml@kongu.ac.in"},
            {"name": "Ms. R. Subapriya", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Data Mining, Object Oriented Programming Systems", "email": "subapriya.aiml@kongu.ac.in"},
            {"name": "Dr. M. Mohanasundari", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Deep Learning, Artificial Intelligence", "email": "mohanasundari.aiml@kongu.ac.in"},
            {"name": "Mr. V. Arun Antony", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "VLSI Design, Embedded Systems, Machine Learning Hardware", "email": "arunantony.aiml@kongu.ac.in"},
            {"name": "Ms. A. Vanmathi", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning, Artificial Intelligence, Python Programming", "email": "vanmathi.aiml@kongu.ac.in"},
            {"name": "Ms. B. Kalaivani", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Machine Learning and Data Science, Big Data", "email": "kalaivani.aiml@kongu.ac.in"}
        ]
    },
    {
        "name": "Chemical Engineering",
        "short_code": "CHEM",
        "courses": [
            {"code": "22CHT501", "name": "Chemical Reaction Engineering", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22CHT502", "name": "Heat & Mass Transfer Operations", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22CHT601", "name": "Process Dynamics & Instrumentation Control", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22CHT602", "name": "Wastewater Treatment & Separation Technology", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. KANNAN KANDASAMY", "designation": "SENIOR PROFESSOR", "years_of_experience": 26, "area_of_expertise": "Chemical Reaction Engineering, Waste Water Treatment, Advanced oxidation process, Energy storage Materials", "email": "kannank@kongu.ac.in"},
            {"name": "Dr. V. Sangeetha", "designation": "Professor & Head", "years_of_experience": 16, "area_of_expertise": "Process Engineering, Wastewater Treatment, New product Development", "email": "vsangeetha@kongu.ac.in"},
            {"name": "Dr. C. Gomadurai", "designation": "Senior Associate Professor", "years_of_experience": 22, "area_of_expertise": "Solution Thermodynamics, Environmental Engineering, Separation Technology, Mass Transfer and Process Intensification, Engineering Properties of Materials", "email": "cg@kongu.ac.in"},
            {"name": "Dr. A. S. Periasamy Manikandan", "designation": "Associate Professor", "years_of_experience": 19, "area_of_expertise": "Heat Transfer, Mass Transfer, Petroleum Refining and Petrochemicals", "email": "aspm@kongu.ac.in"},
            {"name": "Dr. G. Mugaishudeen", "designation": "Associate Professor", "years_of_experience": 13, "area_of_expertise": "Multiphase Flow, Wastewater Treatment", "email": "mugais.chem@kongu.ac.in"},
            {"name": "Dr. S. Mothil", "designation": "Associate Professor", "years_of_experience": 9, "area_of_expertise": "Thermochemical Conversion of Biomass, Photocatalysis, Bioprocess Engineering, Pharmaceutical Technology, Optimization using RSM, ANN and Python", "email": "mothil.chem@kongu.ac.in"},
            {"name": "Dr. D. Nesakumar", "designation": "Assistant Professor (SLG)", "years_of_experience": 16, "area_of_expertise": "Chemical Equipment Design, Environmental Engineering, Process Utilities", "email": "nesakumar@kongu.ac.in"},
            {"name": "Mr. R. Sathish Raam", "designation": "Assistant Professor (SLG)", "years_of_experience": 10, "area_of_expertise": "Thermochemical Conversion - HTL, Membrane Separation, Biofuels", "email": "sathishraam.chem@kongu.edu"},
            {"name": "Ms. K. Kalaivani", "designation": "Assistant Professor (SRG)", "years_of_experience": 11, "area_of_expertise": "Biochemical Engineering, Drugs and Pharmaceutical Technology, Bioprocess Engineering, Membrane Separation", "email": "kalaivanik@kongu.ac.in"},
            {"name": "Mr. S. Yuvaraj", "designation": "Assistant Professor", "years_of_experience": 9, "area_of_expertise": "Transport Phenomena, Mass Transfer, Process Instrumentation & Control", "email": "yuvaraj.chem@kongu.ac.in"},
            {"name": "Mr. M. Ismail Shahib", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Carbon Nanomaterial Synthesis, Life Cycle Assessment, Environmental Biotechnology", "email": "ismailshahib.chem@kongu.edu"},
            {"name": "Ms. A. Tamilarasi", "designation": "Assistant Professor", "years_of_experience": 4, "area_of_expertise": "Waste water Treatment, Electrochemical Science, Green Hydrogen Production", "email": "tamilarasi.chem@kongu.edu"}
        ]
    },
    {
        "name": "Food Technology",
        "short_code": "FT",
        "courses": [
            {"code": "22FTT501", "name": "Food Processing Operations & Preservation", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22FTT502", "name": "Dairy Process Engineering", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22FTT601", "name": "Food Packaging and Storage Technology", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22FTT602", "name": "Baking, Confectionery & Beverage Technology", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. R. Baskar", "designation": "Senior Professor & Vice Principal", "years_of_experience": 24, "area_of_expertise": "Process Engineering, Food Processing & Engineering, Bioprocess Technology", "email": "erbaskar@kongu.ac.in"},
            {"name": "Dr. V. Chitra Devi", "designation": "Senior Professor & Head", "years_of_experience": 26, "area_of_expertise": "Biofuels, Bioprocess Engineering, Environmental Engineering, Food Biotechnology", "email": "chitrasuresh@kongu.ac.in"},
            {"name": "Dr. K. Senthilkumar", "designation": "Senior Associate Professor", "years_of_experience": 25, "area_of_expertise": "Waste Valorization, Microbial Fuel Cell, Food Processing, Fermentation Technology", "email": "senthilkumar.chem@kongu.ac.in"},
            {"name": "Mr. M. S. Shivaswamy", "designation": "Assistant Professor (SRG)", "years_of_experience": 15, "area_of_expertise": "Dairy Engineering, Food Process Engineering, Food Quality & Safety", "email": "msswamy@kongu.ac.in"},
            {"name": "Mr. J. Jony Blessing Manoj", "designation": "Assistant Professor (SRG)", "years_of_experience": 11, "area_of_expertise": "Food Packaging Technology, Meat Fish and Poultry Processing, Food Preservation", "email": "manoj.ft@kongu.ac.in"},
            {"name": "Mr. V. Arun Joshy", "designation": "Assistant Professor (SRG)", "years_of_experience": 6, "area_of_expertise": "Food Technology, Food Analysis, Post Harvest Technology", "email": "arunjoshy.ft@kongu.ac.in"},
            {"name": "Ms. N. Dhivya Bharathi", "designation": "Assistant Professor (SRG)", "years_of_experience": 7, "area_of_expertise": "Drying Technology, Beverage Technology, Food Product Development", "email": "dhivyabharathi.ft@kongu.ac.in"},
            {"name": "Ms. K. K. Sri Mohana Priya", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Drying Technology, Extraction of bioactive compounds, Food Chemistry", "email": "mohanapriya.ft@kongu.ac.in"},
            {"name": "Ms. R. M. Deepika", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Baking and Confectionery Technology, Food Safety and Quality Assurance", "email": "deepika.ft@kongu.ac.in"},
            {"name": "Ms. S. Kavinya", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Food Packaging Technology, Baking and Confectionery, Food Microbiology", "email": "kavinya.ft@kongu.ac.in"},
            {"name": "Ms. M. Mohana Priya", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "New product development, Food process Engineering, Fruit & Vegetable Processing", "email": "mmohanapriya.ft@kongu.ac.in"},
            {"name": "Ms. M. Ramya", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Novel Food Processing Technology, New product development, Food Rheology", "email": "ramya.ft@kongu.ac.in"},
            {"name": "Ms. G. Preethi", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "New product development, Food chemistry, Food Toxicology", "email": "preethi.ft@kongu.ac.in"},
            {"name": "Ms. M. Poorvitha", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Food Packaging Technology, Dairy Technology, Functional Foods", "email": "poorvitha.ft@kongu.ac.in"},
            {"name": "Ms. G. Kiruthika", "designation": "Assistant Professor", "years_of_experience": 6, "area_of_expertise": "Food Technology, Food Safety Regulations, Food Preservation Techniques", "email": "kiruthika.ft@kongu.ac.in"}
        ]
    },
    {
        "name": "Mechatronics Engineering",
        "short_code": "MTS",
        "courses": [
            {"code": "22MTT501", "name": "Sensors, Actuators & Signal Conditioning", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22MTT502", "name": "Microcontrollers & PLC Automation", "semester": "Semester 5", "academic_year": "2025-2026"},
            {"code": "22MTT601", "name": "Robotics & Machine Vision Systems", "semester": "Semester 6", "academic_year": "2025-2026"},
            {"code": "22MTT602", "name": "Automotive Electronics & Electric Drives", "semester": "Semester 6", "academic_year": "2025-2026"}
        ],
        "faculty": [
            {"name": "Dr. B. Meenakshipriya", "designation": "Senior Professor & Dean", "years_of_experience": 22, "area_of_expertise": "Mechatronics, Non Linear Control System, Process Control & Instrumentation", "email": "bmp@kongu.ac.in"},
            {"name": "Dr. C. Jegadheesan", "designation": "Professor & Head", "years_of_experience": 20, "area_of_expertise": "Automotive Electronics and Control Systems, Electric Vehicles, Embedded Systems", "email": "cjegadheesan.auto@kongu.ac.in"},
            {"name": "Dr. N. Nithyavathy", "designation": "Professor", "years_of_experience": 20, "area_of_expertise": "Control System Engineering, Nanoscience and Technology, Robotics", "email": "nithyavathy@kongu.ac.in"},
            {"name": "Dr. P. Ravichandran", "designation": "Associate Professor", "years_of_experience": 17, "area_of_expertise": "Mechatronics Engineering, Manufacturing Systems, CNC & CAM", "email": "ravichandran@kongu.ac.in"},
            {"name": "Dr. S. K. Thangarasu", "designation": "Associate Professor", "years_of_experience": 16, "area_of_expertise": "Mechatronics, Industrial Automation, PLC and SCADA", "email": "thangarasu@kongu.ac.in"},
            {"name": "Dr. S. Praveen Kumar", "designation": "Associate Professor", "years_of_experience": 13, "area_of_expertise": "Engineering Design, Theory of Machines, Kinematics & Dynamics", "email": "praveenkumar.mts@kongu.edu"},
            {"name": "Dr. N. Muralidharan", "designation": "Associate Professor", "years_of_experience": 18, "area_of_expertise": "Mechatronics Engineering, Sensors and Actuators, Microcontrollers", "email": "muralimts@kongu.ac.in"},
            {"name": "Dr. T. Tamilarasi", "designation": "Associate Professor", "years_of_experience": 17, "area_of_expertise": "Mechatronics, Thin Film Coating, Material Science", "email": "tamilravi@kongu.ac.in"},
            {"name": "Dr. R. Nithyaprakash", "designation": "Associate Professor", "years_of_experience": 10, "area_of_expertise": "Tribology, Biomaterials, Finite Element Analysis", "email": "nithyaprakash.mts@kongu.ac.in"},
            {"name": "Dr. A. Shanmugam", "designation": "Assistant Professor (SLG)", "years_of_experience": 16, "area_of_expertise": "Advanced Manufacturing Technology, Precision Engineering", "email": "shanmugam@kongu.ac.in"},
            {"name": "Dr. S. Arun Kumar", "designation": "Assistant Professor (SLG)", "years_of_experience": 12, "area_of_expertise": "Automotive Electronics, Industrial Automation, Embedded Systems", "email": "sarunkumar@kongu.ac.in"},
            {"name": "Dr. S. Thangavel", "designation": "Assistant Professor (SLG)", "years_of_experience": 10, "area_of_expertise": "Industrial Automation, Electrical Machines and Drives", "email": "thangavel.mts@kongu.ac.in"},
            {"name": "Mr. C. Anbu", "designation": "Assistant Professor (SLG)", "years_of_experience": 25, "area_of_expertise": "Plant Maintenance, Welding & Non-Traditional Machining, Hydraulics and Pneumatics", "email": "anbu.mts@kongu.edu"},
            {"name": "Dr. P. M. Arunkumar", "designation": "Assistant Professor (SLG)", "years_of_experience": 9, "area_of_expertise": "Engineering Design, Optimization Techniques, CAD Modeling", "email": "arunkumarpm.mts@kongu.edu"},
            {"name": "Dr. S. Raghavendra Prabhu", "designation": "Assistant Professor (SLG)", "years_of_experience": 14, "area_of_expertise": "Mechatronics, Engineering Design, Vibration Analysis", "email": "raghavendra.mts@kongu.ac.in"},
            {"name": "Mr. T. Karthik", "designation": "Assistant Professor (SRG)", "years_of_experience": 13, "area_of_expertise": "Advanced Manufacturing Process, Automotive Engineering, Rapid Prototyping", "email": "karthik.mts@kongu.ac.in"},
            {"name": "Dr. K. V. Mahesh Kumar", "designation": "Assistant Professor (SRG)", "years_of_experience": 19, "area_of_expertise": "Manufacturing Engineering, Polymer Composites, Machining", "email": "maheshkumar.mts@kongu.ac.in"},
            {"name": "Mr. T. Surendran", "designation": "Assistant Professor", "years_of_experience": 3, "area_of_expertise": "Process Control, Soft Computing, Industrial Instrumentation", "email": "surendran.eie@kongu.ac.in"},
            {"name": "Mr. S. Santhosh Kumar", "designation": "Assistant Professor", "years_of_experience": 15, "area_of_expertise": "Product Design & Development, CAD/CAM, Mechanics of Solids", "email": "santhosh.mts@kongu.ac.in"},
            {"name": "Mr. G. Raja", "designation": "Assistant Professor", "years_of_experience": 7, "area_of_expertise": "Engineering Design, Thermal Analysis, Machine Dynamics", "email": "raja.mech@kongu.ac.in"},
            {"name": "Ms. K. K. Megavarthini", "designation": "Assistant Professor", "years_of_experience": 9, "area_of_expertise": "Additive Manufacturing, Biomechatronics, 3D Printing", "email": "megavarthini.mts@kongu.ac.in"},
            {"name": "Ms. K. Ezhilarasi", "designation": "Assistant Professor", "years_of_experience": 10, "area_of_expertise": "Instrumentation and Control Engineering, Sensor Technology", "email": "ezhilarasi.mts@kongu.ac.in"}
        ]
    }
]

# Additional CSD faculties from PDF if not already present
CSD_EXTRA = [
    {"name": "Mr. P. Gowsikraja", "designation": "Assistant Professor", "years_of_experience": 2, "area_of_expertise": "Deep Learning, Full Stack Development", "email": "gowsikraja.csd@kongu.ac.in"},
    {"name": "Ms. A. Nivetha", "designation": "Assistant Professor", "years_of_experience": 1, "area_of_expertise": "Computer Organization, VLSI", "email": "nivetha.csd@kongu.ac.in"}
]

with app.app_context():
    # 1. Update CSD if needed
    csd_dept = Department.query.filter_by(short_code="CSD").first()
    if csd_dept:
        for f_extra in CSD_EXTRA:
            existing = Faculty.query.filter_by(email=f_extra["email"].lower().strip()).first()
            if not existing:
                f_obj = Faculty(
                    name=f_extra["name"],
                    email=f_extra["email"].lower().strip(),
                    designation=f_extra["designation"],
                    years_of_experience=f_extra["years_of_experience"],
                    area_of_expertise=f_extra["area_of_expertise"],
                    department_id=csd_dept.id,
                    is_active=True
                )
                db.session.add(f_obj)
                print(f"Added extra CSD faculty: {f_extra['name']}")

    # 2. Add new departments, courses, and faculties
    total_depts_added = 0
    total_facs_added = 0
    total_courses_added = 0

    for d_info in NEW_DATA:
        dept = Department.query.filter_by(short_code=d_info["short_code"]).first()
        if not dept:
            dept = Department(name=d_info["name"], short_code=d_info["short_code"])
            db.session.add(dept)
            db.session.flush()
            total_depts_added += 1
            print(f"Created department: {dept.name} ({dept.short_code}) with ID {dept.id}")
        else:
            print(f"Department exists: {dept.name} ({dept.short_code}) with ID {dept.id}")

        # Courses
        for c_info in d_info["courses"]:
            c_existing = Course.query.filter_by(code=c_info["code"]).first()
            if not c_existing:
                c = Course(
                    name=c_info["name"],
                    code=c_info["code"],
                    semester=c_info["semester"],
                    academic_year=c_info["academic_year"],
                    department_id=dept.id,
                    status="Pending"
                )
                db.session.add(c)
                total_courses_added += 1

        # Faculties
        for f_info in d_info["faculty"]:
            clean_email = f_info["email"].lower().strip()
            # Enforce institutional domain validation
            if not (clean_email.endswith('@kongu.edu') or clean_email.endswith('@kongu.ac.in')):
                raise ValueError(f"Invalid email domain for faculty {f_info['name']}: {clean_email}")
            
            f_existing = Faculty.query.filter_by(email=clean_email).first()
            if not f_existing:
                f = Faculty(
                    name=f_info["name"],
                    email=clean_email,
                    designation=f_info["designation"],
                    years_of_experience=f_info["years_of_experience"],
                    area_of_expertise=f_info["area_of_expertise"],
                    department_id=dept.id,
                    is_active=True
                )
                db.session.add(f)
                total_facs_added += 1

    db.session.commit()
    print(f"\nSuccessfully committed changes to database:")
    print(f"  New Departments Added: {total_depts_added}")
    print(f"  New Courses Added: {total_courses_added}")
    print(f"  New Faculty Added: {total_facs_added}")

    # Synchronize instance DB to kongu_expert_panel.db
    instance_db = os.path.join(app.instance_path, "expert_panel.db")
    backup_db = os.path.join(os.path.dirname(app.instance_path), "kongu_expert_panel.db")
    if os.path.exists(instance_db):
        shutil.copy2(instance_db, backup_db)
        print(f"Synchronized database copy to {backup_db}")

    # Summary of all departments
    all_depts = Department.query.order_by(Department.id).all()
    print("\n================== CURRENT DATABASE SUMMARY ==================")
    total_fac_count = 0
    for d in all_depts:
        count = Faculty.query.filter_by(department_id=d.id).count()
        total_fac_count += count
        print(f"Department {d.id:2d}: [{d.short_code:4s}] {d.name:<45} -> {count:3d} faculties")
    print(f"--------------------------------------------------------------")
    print(f"Total Departments: {len(all_depts)}")
    print(f"Total Faculties:   {total_fac_count}")
    print("==============================================================")
