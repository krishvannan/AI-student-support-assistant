"""
Sample Document Generator for CampusAI.
Generates realistic college PDFs using ReportLab for testing RAG, summarization, and quiz generation.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from utils.config import DOCUMENTS_DIR


def create_sample_documents():
    """Generate 5 realistic college PDF documents in the documents/ directory."""
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f2b48'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )
    heading2_style = ParagraphStyle(
        'DocHeading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        spaceAfter=4
    )

    # -------------------------------------------------------------
    # 1. Academic Regulations 2024
    # -------------------------------------------------------------
    doc1_path = DOCUMENTS_DIR / "academic_regulations_2024.pdf"
    doc1 = SimpleDocTemplate(str(doc1_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story1 = [
        Paragraph("NATIONAL INSTITUTE OF TECHNOLOGY & ADVANCED STUDIES", title_style),
        Paragraph("<b>ACADEMIC REGULATIONS & POLICIES (R-2024)</b><br/>For All Undergraduate Engineering Programmes (B.Tech / B.E.)", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=12),

        Paragraph("Article 1: Attendance Requirements and Condonation Policy", heading2_style),
        Paragraph("1.1 Every student is expected to attend 100% of all theory, tutorial, and practical classes. However, to account for unforeseen contingencies, a minimum aggregate attendance of <b>75%</b> across all registered courses is strictly mandatory to be eligible to appear in End-Semester Examinations (ESE).", body_style),
        Paragraph("1.2 <b>Medical Condonation:</b> Students having attendance between <b>65% and 74.9%</b> on valid medical grounds, approved university sports/cultural representation, or serious family emergencies may apply for condonation. The condonation application must be submitted along with an authorized medical certificate to the Head of Department within <b>5 working days</b> of resuming classes, accompanied by a condonation fee of <b>Rs. 1,000</b>.", body_style),
        Paragraph("1.3 <b>Detention:</b> Students whose aggregate attendance falls below <b>65%</b> are strictly not eligible for condonation under any circumstances. Such students will be detained, will not be permitted to write the end-semester examinations, and must re-register and repeat the semester in the subsequent academic year.", body_style),

        Paragraph("Article 2: 10-Point Absolute Grading System", heading2_style),
        Paragraph("The academic performance of a student is evaluated using a 10-point letter grading system:", body_style)
    ]

    grade_data = [
        ["Grade", "Performance Description", "Marks Range", "Grade Point (GP)"],
        ["O", "Outstanding", "91 - 100", "10"],
        ["A+", "Excellent", "81 - 90", "9"],
        ["A", "Very Good", "71 - 80", "8"],
        ["B+", "Good", "61 - 70", "7"],
        ["B", "Above Average", "50 - 60", "6"],
        ["RA", "Re-Appearance (Fail)", "< 50", "0"],
        ["SA", "Shortage of Attendance (Detained)", "-", "0"],
        ["W", "Withdrawal from Examination", "-", "0"]
    ]
    t1 = Table(grade_data, colWidths=[60, 200, 120, 120])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story1.append(t1)
    story1.append(Spacer(1, 10))

    story1.extend([
        Paragraph("Article 3: Assessment Pattern & Weightages", heading2_style),
        Paragraph("3.1 <b>Continuous Internal Assessment (CIA): 40% Weightage</b> comprising three Continuous Assessment Tests (CAT-1, CAT-2, CAT-3) of 15% each (best two considered for 30%), plus 10% for assignments, quizzes, and mini-projects.", body_style),
        Paragraph("3.2 <b>End-Semester Examination (ESE): 60% Weightage</b> conducted as a 3-hour centralized written examination covering all course units.", body_style),
        Paragraph("3.3 Minimum passing criterion: A student must secure at least <b>45%</b> marks in the End-Semester Examination and at least <b>50%</b> marks in aggregate (CIA + ESE combined) to pass a course.", body_style),

        Paragraph("Article 4: Re-evaluation & Answer Script Photocopy", heading2_style),
        Paragraph("Candidates who wish to apply for re-evaluation of theory courses must apply for a photocopy of their evaluated answer script within <b>7 days</b> of result declaration (Fee: Rs. 300 per script). Re-evaluation application must be submitted within <b>5 days</b> after receiving the photocopy with a fee of <b>Rs. 500 per subject</b>. If re-evaluation results in an increase of 15% or more, 50% of the re-evaluation fee will be refunded.", body_style),

        Paragraph("Article 5: Policy on Malpractice in Examinations", heading2_style),
        Paragraph("Any candidate found possessing unauthorized materials (notes, mobile phones, smartwatches) inside the examination hall will face immediate cancellation of that specific examination. Level-2 malpractice (copying or impersonation) leads to cancellation of all examinations of that semester and debarment for one full academic year.", body_style)
    ])
    doc1.build(story1)

    # -------------------------------------------------------------
    # 2. CSE Curriculum and Syllabus (Semester 6)
    # -------------------------------------------------------------
    doc2_path = DOCUMENTS_DIR / "cse_curriculum_and_syllabus.pdf"
    doc2 = SimpleDocTemplate(str(doc2_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story2 = [
        Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", title_style),
        Paragraph("<b>BE-CSE CURRICULUM AND DETAILED SYLLABUS - SEMESTER 6</b><br/>Academic Year 2024-2025", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=12),

        Paragraph("Course 1: CS8601 - Artificial Intelligence & Machine Learning (Credits: 4)", heading2_style),
        Paragraph("<b>Course Objectives:</b> To understand intelligent agents, search algorithms, knowledge representation, supervised learning, neural networks, and modern transformers.", body_style),
        Paragraph("• <b>Unit 1 - Intelligent Agents & Heuristic Search:</b> Agents and environments, State space search, BFS, DFS, Heuristic search, A* algorithm, AO* search, Adversarial search, Minimax with Alpha-Beta pruning.", bullet_style),
        Paragraph("• <b>Unit 2 - Knowledge Representation & Reasoning:</b> First-order predicate logic, Unification, Resolution refutation, Bayesian networks, Hidden Markov Models, Dempster-Shafer theory.", bullet_style),
        Paragraph("• <b>Unit 3 - Classical Machine Learning:</b> Supervised vs Unsupervised learning, Linear and Logistic Regression, Decision Trees (ID3, CART), Support Vector Machines (SVM), Random Forests, K-Means clustering.", bullet_style),
        Paragraph("• <b>Unit 4 - Deep Learning Foundations:</b> Feedforward Neural Networks, Backpropagation, CNN for Computer Vision, RNN, LSTM, and GRU for sequential data.", bullet_style),
        Paragraph("• <b>Unit 5 - Generative AI & LLMs:</b> Attention mechanism, Transformer architecture, Self-attention, Pre-trained language models (BERT, GPT), Prompt engineering, RAG architecture.", bullet_style),
        Paragraph("<b>Prescribed Textbooks:</b> Stuart Russell & Peter Norvig, 'Artificial Intelligence: A Modern Approach', 4th Edition; Ian Goodfellow, 'Deep Learning', MIT Press.", body_style),

        Paragraph("Course 2: CS8602 - Cloud Computing & Distributed Systems (Credits: 3)", heading2_style),
        Paragraph("• <b>Unit 1 - Cloud Architecture & Models:</b> NIST cloud definitions, IaaS, PaaS, SaaS, Public, Private, Hybrid clouds, Virtualization (Hypervisors Type 1 & 2), Containerization using Docker.", bullet_style),
        Paragraph("• <b>Unit 2 - Cloud Orchestration & Microservices:</b> Kubernetes clusters, pods, deployments, Service Mesh, RESTful microservice communication, API gateways.", bullet_style),
        Paragraph("• <b>Unit 3 - Distributed Data Processing:</b> Hadoop architecture, HDFS, MapReduce programming paradigm, Apache Spark distributed in-memory computations.", bullet_style),
        Paragraph("• <b>Unit 4 - Cloud Storage & Security:</b> Object storage (AWS S3), NoSQL stores, IAM roles, Data encryption in transit and at rest, Cloud disaster recovery.", bullet_style),
        Paragraph("<b>Prescribed Textbooks:</b> Rajkumar Buyya, 'Mastering Cloud Computing', McGraw Hill.", body_style),

        Paragraph("Course 3: CS8603 - Compiler Design (Credits: 4)", heading2_style),
        Paragraph("• <b>Unit 1 - Lexical Analysis:</b> Regular expressions, Finite Automata (DFA, NFA), Lex lexical analyzer generator.", bullet_style),
        Paragraph("• <b>Unit 2 - Syntax Analysis:</b> Context-free grammars, Top-down parsing (LL(1)), Bottom-up parsing (Shift-reduce, LR(0), SLR, CLR, LALR parsers), Yacc parser generator.", bullet_style),
        Paragraph("• <b>Unit 3 - Syntax-Directed Translation & Type Checking:</b> Syntax-directed definitions, S-attributed and L-attributed definitions, Intermediate code representations (Three-address code, Quadruples, Triples).", bullet_style),
        Paragraph("• <b>Unit 4 - Code Optimization & Generation:</b> Basic blocks and flow graphs, Loop optimization, Common subexpression elimination, Dead code elimination, Register allocation and assignment.", bullet_style),
        Paragraph("<b>Prescribed Textbooks:</b> Alfred Aho, Monica Lam, Ravi Sethi, Jeffrey Ullman, 'Compilers: Principles, Techniques, and Tools' (Dragon Book), 2nd Edition.", body_style),

        Paragraph("Course 4: CS8604 - Web Technologies & Full-Stack Development (Credits: 3)", heading2_style),
        Paragraph("Modern web architecture, HTML5 semantic elements, responsive CSS with Flexbox and Grid, modern ES6+ JavaScript, React component state lifecycle, Node.js and Express backend API design, MongoDB integration, JWT authentication.", body_style)
    ]
    doc2.build(story2)

    # -------------------------------------------------------------
    # 3. Campus Placement Circular 2024
    # -------------------------------------------------------------
    doc3_path = DOCUMENTS_DIR / "campus_placement_circular_2024.pdf"
    doc3 = SimpleDocTemplate(str(doc3_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story3 = [
        Paragraph("CENTRE FOR CAREER ADVANCEMENT & PLACEMENT", title_style),
        Paragraph("<b>CAMPUS RECRUITMENT CIRCULAR - BATCH 2025</b><br/>Ref. No: CCAP/2024/CIR-088 | Date: October 14, 2024", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=12),

        Paragraph("Subject: Mega Placement Drive - Tier-1 Tech Giants & IT Services", heading2_style),
        Paragraph("This is to inform all final-year and pre-final year students that registration is officially open for the upcoming Mega On-Campus Placement Drive for recruitment by <b>TCS Digital, Google Cloud India, Infosys Specialist Programmer, and Microsoft IDC</b>.", body_style),

        Paragraph("1. Eligibility Criteria", heading2_style),
        Paragraph("• Eligible Disciplines: B.E. / B.Tech in <b>Computer Science (CSE), Information Technology (IT), Electronics & Communication (ECE), and AI & Data Science (AI&DS)</b>.", bullet_style),
        Paragraph("• Academic Cutoff: Aggregate CGPA of <b>7.50 and above</b> up to the 6th semester without any active standing backlogs/arrears.", bullet_style),
        Paragraph("• Secondary Education: Minimum 75% marks in Class 10th and 12th Board examinations.", bullet_style),

        Paragraph("2. Registration Details & Strict Deadline", heading2_style),
        Paragraph("Eligible candidates must submit their application on the University Placement ERP Portal (<b>https://placement.university.edu/login</b>) and upload an updated single-page technical resume.", body_style),
        Paragraph("• <b>Registration Closes: Friday, October 25, 2024 at 5:00 PM Sharp.</b><br/>Late entries or requests by email will NOT be entertained under any circumstances.", body_style)
    ]

    drive_schedule = [
        ["Phase / Round", "Scheduled Date", "Mode & Venue", "Evaluation Focus"],
        ["Round 1: Online Assessment", "Nov 03, 2024 (10:00 AM)", "University Central Computing Lab", "DSA, Coding, Aptitude, Core CS"],
        ["Round 2: Technical Interview", "Nov 10 - Nov 12, 2024", "Academic Block B, Floor 3", "System Design, Projects, Live Coding"],
        ["Round 3: HR & Managerial", "Nov 15, 2024", "Conference Hall 1", "Communication, Behavioral, Cultural Fit"],
        ["Offer Announcements", "Nov 18, 2024", "ERP Portal Notification", "Final Shortlist & CTC packages"]
    ]
    t3 = Table(drive_schedule, colWidths=[120, 110, 130, 150])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b48')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story3.append(t3)
    story3.append(Spacer(1, 10))

    story3.extend([
        Paragraph("3. Mandatory Student Preparation & Documents Required", heading2_style),
        Paragraph("• Candidates must report in strict western formal attire.", bullet_style),
        Paragraph("• Carry 3 printed copies of verified resume, 4 passport photos, and valid College ID card.", bullet_style),
        Paragraph("• For technical inquiries: Contact Placement Coordinator at <b>placement@university.edu.in</b> or visit Room 302, Academic Block B.", bullet_style)
    ])
    doc3.build(story3)

    # -------------------------------------------------------------
    # 4. End Semester Examination Notice
    # -------------------------------------------------------------
    doc4_path = DOCUMENTS_DIR / "end_semester_examination_notice.pdf"
    doc4 = SimpleDocTemplate(str(doc4_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story4 = [
        Paragraph("OFFICE OF THE CONTROLLER OF EXAMINATIONS", title_style),
        Paragraph("<b>EXAMINATION NOTIFICATION & TIMETABLE NOTICE</b><br/>Circular No: COE/2024/ES-02 | Academic Year: 2024-25", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=12),

        Paragraph("Subject: Schedule for November / December 2024 Regular & Arrear Examinations", heading2_style),
        Paragraph("All undergraduate and postgraduate students are hereby notified regarding the timeline for the upcoming Semester Examinations (Practical and Theory):", body_style),

        Paragraph("1. Important Dates & Fee Deadlines", heading2_style),
        Paragraph("• <b>Online Exam Fee Payment (Without Late Fee):</b> October 10, 2024 to <b>October 24, 2024</b>.", bullet_style),
        Paragraph("• <b>Fee Payment with Late Penalty (Rs. 500):</b> October 25, 2024 to <b>October 29, 2024</b>.", bullet_style),
        Paragraph("• <b>Final Cloture of Portal:</b> October 30, 2024 (No fees accepted after this date).", bullet_style),
        Paragraph("• <b>Hall Ticket Release & Download:</b> November 05, 2024 from student portal.", bullet_style),
        Paragraph("• <b>Practical & Laboratory Examinations:</b> November 11, 2024 to November 16, 2024.", bullet_style),
        Paragraph("• <b>Commencement of Written Theory Examinations:</b> <b>November 20, 2024</b>.", bullet_style),

        Paragraph("2. Mandatory Examination Hall Regulations", heading2_style),
        Paragraph("1. <b>Identity Verification:</b> No candidate will be admitted into the examination hall without their official Hall Ticket and valid University Identity Card.", body_style),
        Paragraph("2. <b>Reporting Time:</b> Morning session begins at 10:00 AM (Entry allowed from 9:30 AM). Hall doors will be locked precisely 15 minutes after examination begins (10:15 AM). Latecomers will NOT be permitted.", body_style),
        Paragraph("3. <b>Prohibited Electronic Articles:</b> Mobile phones, smartwatches, digital organizers, Bluetooth earphones, and programmable calculators are strictly banned. Possession of any electronic gadget will result in instant confiscation and booking under University Malpractice Ordinance.", body_style)
    ]
    doc4.build(story4)

    # -------------------------------------------------------------
    # 5. Campus Hostel & Facility Guide
    # -------------------------------------------------------------
    doc5_path = DOCUMENTS_DIR / "campus_hostel_and_facility_guide.pdf"
    doc5 = SimpleDocTemplate(str(doc5_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story5 = [
        Paragraph("CAMPUS WELFARE & STUDENT AFFAIRS COUNCIL", title_style),
        Paragraph("<b>STUDENT HANDBOOK & CAMPUS FACILITIES GUIDE</b><br/>Edition: 2024-2025", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=12),

        Paragraph("1. Dr. A.P.J. Abdul Kalam Central Library", heading2_style),
        Paragraph("• <b>Operating Hours:</b> 8:00 AM to 10:00 PM on all working days; 9:00 AM to 5:00 PM on Saturdays and Sundays. Digital reading room open 24/7 during exam periods.", bullet_style),
        Paragraph("• <b>Borrowing Privileges:</b> Undergraduate students are eligible to borrow up to 4 books simultaneously for an initial period of 15 days, renewable once online.", bullet_style),
        Paragraph("• <b>Overdue Fines:</b> Rs. 2 per day per volume for the first 7 overdue days; Rs. 5 per day thereafter.", bullet_style),

        Paragraph("2. High-Speed Campus Network & IT Services", heading2_style),
        Paragraph("• <b>Wi-Fi SSID:</b> 'CAMPUS-STUDENT-5G' available across academic blocks, libraries, and hostels.", bullet_style),
        Paragraph("• <b>Access Credentials:</b> Login using your University Roll Number and Student Portal Password. BitTorrent and illicit streaming protocols are permanently blocked.", bullet_style),

        Paragraph("3. Resident Hostel Rules & Gate Curfew", heading2_style),
        Paragraph("• <b>Evening Curfew:</b> All resident students must enter hostel premises before <b>8:30 PM</b>. Biometric punch verification is mandatory.", bullet_style),
        Paragraph("• <b>Night Pass / Home Leave:</b> Outstation leave requests must be initiated through the Campus Hostel Mobile App at least <b>24 hours in advance</b> and approved by parent/guardian via SMS OTP.", bullet_style),

        Paragraph("4. 24x7 University Health Centre", heading2_style),
        Paragraph("Located opposite Student Activity Centre, staffed with 2 resident medical officers and qualified nursing personnel. Emergency ambulance helpline: <b>Ext. 108 / +91-9876543210</b>.", body_style),

        Paragraph("5. Grievance Redressal & Anti-Ragging Cell", heading2_style),
        Paragraph("The university enforces a zero-tolerance policy against bullying, harassment, and ragging. Toll-Free National Anti-Ragging Helpline: 1800-180-5522. Campus Internal Complaint Committee Email: <b>grievance@university.edu.in</b>.", body_style)
    ]
    doc5.build(story5)

    print(f"Generated 5 sample documents in {DOCUMENTS_DIR}")
    return [str(doc1_path), str(doc2_path), str(doc3_path), str(doc4_path), str(doc5_path)]


if __name__ == "__main__":
    create_sample_documents()
