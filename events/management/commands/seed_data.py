"""
Comprehensive mock-data seeder for CEMS.
Creates users (all roles), events (all statuses), schedules, registrations,
assessments with questions, submissions, feedback and study materials.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime, timedelta
import random
import uuid


DEPARTMENTS = ['CSE', 'ISE', 'ECE', 'EEE', 'MECH', 'CIVIL']

USERS_SPEC = [
    # Coordinators
    dict(username='coord_cse',  email='coord.cse@cmrit.ac.in',  first_name='Rahul',   last_name='Sharma',    role='EVENT_COORDINATOR', dept='CSE',   pwd='Coord@123'),
    dict(username='coord_ise',  email='coord.ise@cmrit.ac.in',  first_name='Priya',   last_name='Nair',      role='EVENT_COORDINATOR', dept='ISE',   pwd='Coord@123'),
    dict(username='coord_ece',  email='coord.ece@cmrit.ac.in',  first_name='Arun',    last_name='Kumar',     role='EVENT_COORDINATOR', dept='ECE',   pwd='Coord@123'),
    dict(username='coord_mech', email='coord.mech@cmrit.ac.in', first_name='Suresh',  last_name='Patel',     role='EVENT_COORDINATOR', dept='MECH',  pwd='Coord@123'),
    # HODs
    dict(username='hod_cse',    email='hod.cse@cmrit.ac.in',    first_name='Dr. Kesavamoorthy', last_name='R',  role='HOD', dept='CSE',  pwd='Hod@123'),
    dict(username='hod_ise',    email='hod.ise@cmrit.ac.in',    first_name='Dr. Jagadishwari',  last_name='V',  role='HOD', dept='ISE',  pwd='Hod@123'),
    dict(username='hod_ece',    email='hod.ece@cmrit.ac.in',    first_name='Dr. Rajesh',        last_name='M',  role='HOD', dept='ECE',  pwd='Hod@123'),
    # Students
    dict(username='student_01', email='s01@cmrit.ac.in', first_name='Aarav',    last_name='Mehta',   role='STUDENT', dept='CSE',  pwd='Student@123', usn='1CR21CS001'),
    dict(username='student_02', email='s02@cmrit.ac.in', first_name='Sneha',    last_name='Reddy',   role='STUDENT', dept='ISE',  pwd='Student@123', usn='1CR21IS002'),
    dict(username='student_03', email='s03@cmrit.ac.in', first_name='Kiran',    last_name='Gowda',   role='STUDENT', dept='ECE',  pwd='Student@123', usn='1CR21EC003'),
    dict(username='student_04', email='s04@cmrit.ac.in', first_name='Divya',    last_name='Krishnan', role='STUDENT', dept='CSE', pwd='Student@123', usn='1CR21CS004'),
    dict(username='student_05', email='s05@cmrit.ac.in', first_name='Rohan',    last_name='Verma',   role='STUDENT', dept='MECH', pwd='Student@123', usn='1CR21ME005'),
    dict(username='student_06', email='s06@cmrit.ac.in', first_name='Ananya',   last_name='Singh',   role='STUDENT', dept='ISE',  pwd='Student@123', usn='1CR21IS006'),
    dict(username='student_07', email='s07@cmrit.ac.in', first_name='Vikram',   last_name='Rao',     role='STUDENT', dept='ECE',  pwd='Student@123', usn='1CR21EC007'),
    dict(username='student_08', email='s08@cmrit.ac.in', first_name='Preethi',  last_name='Nair',    role='STUDENT', dept='CSE',  pwd='Student@123', usn='1CR21CS008'),
]

EVENTS_SPEC = [
    # FULLY APPROVED events
    dict(
        event_name="National Hackathon 2024 — CodeStorm",
        title="CodeStorm 2024",
        about="A 36-hour national-level hackathon where students compete to build innovative solutions for real-world problems. Open to all engineering branches. Cash prizes worth ₹1,00,000.",
        dept='CSE', mode='OFFLINE', venue='Seminar Hall A, Block C',
        date_offset=-30, budget=120000, reg_fee=500, refresh=15000,
        honorarium=20000, attendees=200, status='PRINCIPAL_APPROVED',
        coord='coord_cse',
    ),
    dict(
        event_name="AI & Machine Learning Workshop",
        title="ML Workshop",
        about="Hands-on 2-day workshop covering Python fundamentals, Scikit-learn, TensorFlow, and real-world ML project development. Beginner friendly. Certificates provided.",
        dept='CSE', mode='OFFLINE', venue='CS Lab 3, Ground Floor',
        date_offset=-15, budget=45000, reg_fee=300, refresh=8000,
        honorarium=15000, attendees=80, status='PRINCIPAL_APPROVED',
        coord='coord_cse',
    ),
    dict(
        event_name="IoT and Embedded Systems Conclave",
        title="IoT Conclave",
        about="An industry-academia meet featuring live demos of IoT devices, Arduino workshops, and keynotes from engineers at Bosch and Siemens. Learn to build smart devices from scratch.",
        dept='ECE', mode='OFFLINE', venue='Electronics Lab, Block B',
        date_offset=-10, budget=65000, reg_fee=200, refresh=10000,
        honorarium=12000, attendees=120, status='PRINCIPAL_APPROVED',
        coord='coord_ece',
    ),
    dict(
        event_name="Data Analytics Bootcamp — Python & Tableau",
        title="Data Analytics Bootcamp",
        about="Intensive 3-day bootcamp on data wrangling with Pandas, statistical analysis, and Tableau dashboard creation. Participants will work on a real dataset from a Bengaluru startup.",
        dept='ISE', mode='ONLINE', meeting_link='https://meet.google.com/abc-defg-hij',
        date_offset=5, budget=30000, reg_fee=0, refresh=0,
        honorarium=10000, attendees=150, status='PRINCIPAL_APPROVED',
        coord='coord_ise',
    ),
    dict(
        event_name="Robotics & Automation Expo 2025",
        title="Robo Expo 2025",
        about="Showcase your robots! Teams demonstrate autonomous and semi-autonomous robots in obstacle navigation, line-following, and pick-and-place challenges. Open to all branches.",
        dept='MECH', mode='OFFLINE', venue='Mechanical Workshop, Block D',
        date_offset=10, budget=90000, reg_fee=400, refresh=12000,
        honorarium=18000, attendees=160, status='PRINCIPAL_APPROVED',
        coord='coord_mech',
    ),
    dict(
        event_name="Cybersecurity Awareness Summit",
        title="CyberSec Summit",
        about="A half-day event covering ethical hacking basics, phishing simulations, and OWASP Top 10 vulnerabilities. Guest lecture by a CERT-In certified security professional.",
        dept='ISE', mode='ONLINE', meeting_link='https://zoom.us/j/987654321',
        date_offset=20, budget=25000, reg_fee=0, refresh=0,
        honorarium=8000, attendees=200, status='PRINCIPAL_APPROVED',
        coord='coord_ise',
    ),
    # HOD APPROVED (awaiting principal)
    dict(
        event_name="Advanced CAD/CAM Design Workshop",
        title="CAD Workshop",
        about="Learn SolidWorks and CATIA for mechanical design. Participants will model and simulate a real engineering component. Industry expert from TCS iON will conduct the session.",
        dept='MECH', mode='OFFLINE', venue='Design Studio, Block D',
        date_offset=25, budget=40000, reg_fee=250, refresh=6000,
        honorarium=10000, attendees=60, status='HOD_APPROVED',
        coord='coord_mech',
    ),
    dict(
        event_name="Web Development Masterclass — React & Django",
        title="WebDev Masterclass",
        about="Full-stack web development course covering React, Django REST Framework, and deployment on AWS. Build a portfolio project in 2 days and get a completion certificate.",
        dept='CSE', mode='OFFLINE', venue='CS Lab 1, Ground Floor',
        date_offset=30, budget=35000, reg_fee=300, refresh=7000,
        honorarium=12000, attendees=100, status='HOD_APPROVED',
        coord='coord_cse',
    ),
    # PENDING
    dict(
        event_name="Entrepreneurship & Startup Bootcamp",
        title="Startup Bootcamp",
        about="A week-long bootcamp mentored by successful CMR alumni founders. Topics include idea validation, lean canvas, pitching, and funding. Winner gets seed funding of ₹50,000.",
        dept='CSE', mode='OFFLINE', venue='Auditorium, Main Block',
        date_offset=45, budget=80000, reg_fee=500, refresh=20000,
        honorarium=25000, attendees=300, status='PENDING',
        coord='coord_cse',
    ),
    dict(
        event_name="Circuit Design & PCB Fabrication Workshop",
        title="PCB Workshop",
        about="Learn to design printed circuit boards using KiCad and EasyEDA. Participants will take home a custom-designed PCB. Includes free PCB printing for first 30 registrations.",
        dept='ECE', mode='OFFLINE', venue='Electronics Lab 2, Block B',
        date_offset=40, budget=28000, reg_fee=300, refresh=5000,
        honorarium=8000, attendees=50, status='PENDING',
        coord='coord_ece',
    ),
    # HOD REJECTED
    dict(
        event_name="International Conference on Quantum Computing",
        title="Quantum Conf",
        about="A 3-day international conference on quantum algorithms, quantum cryptography, and post-quantum security. Speakers from MIT and IISc.",
        dept='CSE', mode='OFFLINE', venue='Auditorium',
        date_offset=-60, budget=500000, reg_fee=2000, refresh=50000,
        honorarium=100000, attendees=500, status='HOD_REJECTED',
        coord='coord_cse',
        rejection_reason="Budget exceeds departmental allocation for this academic year. Please revise and resubmit.",
    ),
]

QUESTIONS_BANK = {
    'CSE': [
        ("What does OOP stand for?", [("Object-Oriented Programming", True), ("Open Operating Protocol", False), ("Object-Oriented Protocol", False), ("Online Operational Programming", False)]),
        ("Which data structure uses LIFO?", [("Stack", True), ("Queue", False), ("Array", False), ("Linked List", False)]),
        ("What is the time complexity of binary search?", [("O(log n)", True), ("O(n)", False), ("O(n²)", False), ("O(1)", False)]),
        ("Which Python keyword is used to define a function?", [("def", True), ("func", False), ("function", False), ("define", False)]),
        ("What does SQL stand for?", [("Structured Query Language", True), ("Simple Query Language", False), ("Standard Query Logic", False), ("Structured Question Language", False)]),
    ],
    'ECE': [
        ("What is the unit of electrical resistance?", [("Ohm", True), ("Volt", False), ("Ampere", False), ("Watt", False)]),
        ("Which law states V = IR?", [("Ohm's Law", True), ("Kirchhoff's Law", False), ("Faraday's Law", False), ("Newton's Law", False)]),
        ("What does AM stand for in radio?", [("Amplitude Modulation", True), ("Audio Modulation", False), ("Analog Modulation", False), ("Automatic Modulation", False)]),
    ],
    'ML': [
        ("Which algorithm is used for classification?", [("Decision Tree", True), ("K-Means", False), ("PCA", False), ("DBSCAN", False)]),
        ("What does CNN stand for?", [("Convolutional Neural Network", True), ("Computed Neural Node", False), ("Connected Network Node", False), ("Clustered Neural Net", False)]),
        ("What is overfitting?", [("Model performs well on training but poorly on test", True), ("Model performs poorly on training data", False), ("Model generalizes perfectly", False), ("Model with too few parameters", False)]),
    ],
    'DEFAULT': [
        ("What is the capital of Karnataka?", [("Bengaluru", True), ("Mumbai", False), ("Delhi", False), ("Chennai", False)]),
        ("CMR Institute of Technology is affiliated to?", [("VTU", True), ("Anna University", False), ("JNTU", False), ("Mumbai University", False)]),
        ("What does NAAC stand for?", [("National Assessment and Accreditation Council", True), ("National Academic Achievement Council", False), ("National Association for Academic Certification", False), ("None of the above", False)]),
    ],
}


class Command(BaseCommand):
    help = 'Seed comprehensive mock data for CEMS demo'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing event data before seeding')

    def handle(self, *args, **options):
        from users.models import CustomUser
        from events.models import (
            Event, EventSchedule, EventRegistration, EventFeedback,
            EventMaterial, EventAssessment, Question, QuestionOption,
            AssessmentSubmission, StudentAnswer,
        )

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            for M in [StudentAnswer, AssessmentSubmission, QuestionOption, Question,
                      EventAssessment, EventFeedback, EventMaterial,
                      EventRegistration, EventSchedule, Event]:
                M.objects.delete()
            self.stdout.write(self.style.WARNING('Cleared all event data'))

        # ── Create users ──────────────────────────────────────────────────────
        self.stdout.write('Creating users...')
        user_map = {}
        for spec in USERS_SPEC:
            existing = CustomUser.objects(username=spec['username']).first()
            if not existing:
                u = CustomUser.create_user(
                    username=spec['username'],
                    email=spec['email'],
                    password=spec['pwd'],
                    first_name=spec['first_name'],
                    last_name=spec['last_name'],
                    role=spec['role'],
                    department=spec['dept'],
                )
                if spec.get('usn'):
                    u.usn = spec['usn']
                    u.save()
                user_map[spec['username']] = u
                self.stdout.write(f'  Created {spec["role"]}: {spec["username"]}')
            else:
                user_map[spec['username']] = existing
                self.stdout.write(f'  Exists: {spec["username"]}')

        # Grab existing seeded users
        for existing_uname in ['admin', 'testuser1']:
            u = CustomUser.objects(username=existing_uname).first()
            if u:
                user_map[existing_uname] = u

        students = [v for k, v in user_map.items() if v.role == 'STUDENT']

        # ── Create events ─────────────────────────────────────────────────────
        self.stdout.write('Creating events...')
        event_objs = []
        for i, spec in enumerate(EVENTS_SPEC):
            eid = f"CMRIT-{spec['dept']}-{2024 + i//4:04d}-{(i % 99)+1:03d}"
            if Event.objects(event_id=eid).first():
                ev = Event.objects(event_id=eid).first()
                event_objs.append(ev)
                self.stdout.write(f'  Exists: {eid}')
                continue

            coord = user_map.get(spec['coord'])
            ev_date = date.today() + timedelta(days=spec['date_offset'])
            ev = Event(
                name=spec['event_name'],
                event_name=spec['event_name'],
                title=spec['title'],
                about=spec['about'],
                coordinator=coord,
                department=spec['dept'],
                mode=spec['mode'],
                venue=spec.get('venue'),
                meeting_link=spec.get('meeting_link'),
                date=ev_date,
                time='10:00',
                expected_attendees=spec['attendees'],
                budget=spec['budget'],
                registration_fee=spec['reg_fee'],
                refreshment=spec['refresh'],
                honorarium=spec['honorarium'],
                renumeration=0,
                other_requirements='',
                status=spec['status'],
                event_id=eid,
            )
            if spec.get('rejection_reason'):
                ev.rejection_reason = spec['rejection_reason']
            if spec['status'] in ('HOD_APPROVED', 'PRINCIPAL_APPROVED'):
                ev.hod_approval_date = timezone.now() - timedelta(days=abs(spec['date_offset']) // 2)
            if spec['status'] == 'PRINCIPAL_APPROVED':
                ev.principal_approval_date = timezone.now() - timedelta(days=abs(spec['date_offset']) // 3)
            ev.save()
            event_objs.append(ev)
            self.stdout.write(f'  Created: {eid} — {spec["status"]}')

        # Approved events for registration
        approved_events = [e for e in event_objs if e.status == 'PRINCIPAL_APPROVED']

        # ── Event schedules ───────────────────────────────────────────────────
        self.stdout.write('Creating event schedules...')
        for ev in approved_events[:4]:
            if EventSchedule.objects(event=ev).count() == 0:
                sessions = [
                    ('Registration & Breakfast', '09:00', '09:30'),
                    ('Inaugural Ceremony & Keynote', '09:30', '10:30'),
                    ('Technical Session I', '10:30', '12:30'),
                    ('Lunch Break', '12:30', '13:30'),
                    ('Technical Session II / Workshop', '13:30', '15:30'),
                    ('Q&A and Networking', '15:30', '16:00'),
                    ('Valedictory & Prize Distribution', '16:00', '17:00'),
                ]
                for sname, st, en in sessions:
                    EventSchedule(event=ev, session_name=sname, start_time=st, end_time=en).save()
                self.stdout.write(f'  Sessions added for: {ev.event_name[:40]}')

        # ── Event materials ───────────────────────────────────────────────────
        self.stdout.write('Creating study materials...')
        materials_spec = [
            ("Python Basics Cheat Sheet", "Quick reference for Python syntax and common functions"),
            ("Machine Learning Concepts PDF", "Core ML concepts: supervised, unsupervised, reinforcement learning"),
            ("Data Analytics with Pandas", "Step-by-step guide to data cleaning and analysis with Pandas"),
            ("Workshop Slides — Day 1", "Presentation slides from Day 1 of the workshop"),
            ("Workshop Slides — Day 2", "Presentation slides from Day 2 including hands-on exercises"),
            ("Assessment Sample Questions", "Practice questions to prepare for the post-event assessment"),
        ]
        for ev in approved_events:
            if EventMaterial.objects(event=ev).count() == 0:
                for title, desc in random.sample(materials_spec, k=min(3, len(materials_spec))):
                    EventMaterial(event=ev, title=title, description=desc, file='').save()
                self.stdout.write(f'  Materials for: {ev.event_name[:40]}')

        # ── Registrations ─────────────────────────────────────────────────────
        self.stdout.write('Creating registrations...')
        reg_map = {}  # (event_id, student_id) -> registration
        for ev in approved_events:
            # Register 4–8 students per event
            sample_students = random.sample(students, k=min(random.randint(4, 8), len(students)))
            for stu in sample_students:
                key = (str(ev.id), str(stu.id))
                if not EventRegistration.objects(event=ev, student=stu).first():
                    reg = EventRegistration(
                        event=ev,
                        student=stu,
                        registration_date=timezone.now() - timedelta(days=random.randint(1, 20)),
                    )
                    reg.save()
                    reg_map[key] = reg
                    self.stdout.write(f'  Registered {stu.username} → {ev.event_name[:30]}')
                else:
                    reg = EventRegistration.objects(event=ev, student=stu).first()
                    reg_map[key] = reg

        # ── Assessments & questions ───────────────────────────────────────────
        self.stdout.write('Creating assessments...')
        assessment_objs = []
        for ev in approved_events:
            if EventAssessment.objects(event=ev).count() > 0:
                assessment_objs.extend(list(EventAssessment.objects(event=ev)))
                continue
            a = EventAssessment(
                event=ev,
                title=f"Post-Event Assessment — {ev.title}",
                description=f"Test your knowledge gained during {ev.event_name}. Answer all questions carefully.",
                due_date=timezone.now() + timedelta(days=30),
                total_marks=50,
                passing_score=60,
            )
            a.save()
            assessment_objs.append(a)

            # Add 5 questions
            dept_key = ev.department if ev.department in ('CSE', 'ECE') else 'ML' if ev.department == 'ISE' else 'DEFAULT'
            bank = QUESTIONS_BANK.get(dept_key, QUESTIONS_BANK['DEFAULT'])
            default_bank = QUESTIONS_BANK['DEFAULT']
            pool = (bank + default_bank)[:5]

            for q_text, options in pool:
                q = Question(assessment=a, question_text=q_text, question_type='MCQ', marks=10)
                q.save()
                for opt_text, is_correct in options:
                    QuestionOption(question=q, option_text=opt_text, is_correct=is_correct).save()

            self.stdout.write(f'  Assessment + 5 questions for: {ev.event_name[:40]}')

        # ── Assessment submissions ────────────────────────────────────────────
        self.stdout.write('Creating assessment submissions...')
        for a in assessment_objs:
            registered_students = [
                r.student for r in EventRegistration.objects(event=a.event)
                if r.student
            ]
            questions = list(Question.objects(assessment=a))

            for stu in registered_students[:min(5, len(registered_students))]:
                if AssessmentSubmission.objects(assessment=a, student=stu).first():
                    continue
                score = random.randint(40, 100)
                sub = AssessmentSubmission(
                    assessment=a,
                    student=stu,
                    score=score,
                    submitted_at=timezone.now() - timedelta(days=random.randint(0, 5)),
                )
                sub.save()

                # Mark certificate if score >= passing
                if score >= a.passing_score:
                    reg = EventRegistration.objects(event=a.event, student=stu).first()
                    if reg and not reg.certificate_generated:
                        reg.certificate_generated = True
                        cert_id = uuid.uuid4().hex
                        reg.certificate_url = f"/media/certificates/{a.event.event_id}_{stu.username}_{cert_id}.pdf"
                        reg.save()

                # Create student answers
                for q in questions:
                    opts = list(QuestionOption.objects(question=q))
                    correct_opts = [o for o in opts if o.is_correct]
                    wrong_opts = [o for o in opts if not o.is_correct]
                    # 70% chance of correct answer
                    chosen = correct_opts[0] if (correct_opts and random.random() < 0.7) else (wrong_opts[0] if wrong_opts else None)
                    if chosen:
                        StudentAnswer(
                            submission=sub,
                            question=q,
                            selected_option_ids=[chosen.id],
                            is_correct=chosen.is_correct,
                        ).save()

                self.stdout.write(f'  Submission: {stu.username} → {a.title[:30]} ({score}%)')

        # ── Feedback ──────────────────────────────────────────────────────────
        self.stdout.write('Creating event feedback...')
        feedback_comments = [
            "Excellent event! Very well organized and the speakers were knowledgeable.",
            "Great experience overall. The hands-on sessions were particularly useful.",
            "Loved the workshop! Learned a lot. Would love to attend more such events.",
            "Very informative. The demos were impressive. Minor issue with the internet connection.",
            "Well-organized event with good networking opportunities. Certificates were provided promptly.",
            "Good content but the venue was a bit cramped. Otherwise a great learning experience.",
            "The faculty coordinators did a fantastic job. The schedule was well-managed.",
            "Interesting topics covered. The Q&A session was very engaging and interactive.",
        ]
        for ev in approved_events:
            registered_students = [
                r.student for r in EventRegistration.objects(event=ev)
                if r.student
            ]
            for stu in registered_students[:min(4, len(registered_students))]:
                if EventFeedback.objects(event=ev, student=stu).first():
                    continue
                EventFeedback(
                    event=ev,
                    student=stu,
                    rating=random.randint(3, 5),
                    feedback_text=random.choice(feedback_comments),
                    submitted_date=timezone.now() - timedelta(days=random.randint(0, 10)),
                ).save()
            self.stdout.write(f'  Feedback for: {ev.event_name[:40]}')

        # ── Summary ───────────────────────────────────────────────────────────
        from events.models import Event as E, EventRegistration as ER, EventAssessment as EA
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✔ SEED COMPLETE'))
        self.stdout.write(f'  Users:         {CustomUser.objects.count()}')
        self.stdout.write(f'  Events:        {E.objects.count()}')
        self.stdout.write(f'  Registrations: {ER.objects.count()}')
        self.stdout.write(f'  Assessments:   {EA.objects.count()}')
        self.stdout.write(f'  Submissions:   {AssessmentSubmission.objects.count()}')
        self.stdout.write(f'  Feedback:      {EventFeedback.objects.count()}')
        self.stdout.write('=' * 60)
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Principal   → admin         / Admin@123')
        self.stdout.write('  Coordinator → coord_cse     / Coord@123')
        self.stdout.write('  HOD         → hod_cse       / Hod@123')
        self.stdout.write('  Student     → student_01    / Student@123')
