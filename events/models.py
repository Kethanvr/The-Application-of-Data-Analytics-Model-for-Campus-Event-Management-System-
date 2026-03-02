import mongoengine as me
from users.models import CustomUser


class Event(me.Document):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('HOD_APPROVED', 'HOD Approved'),
        ('HOD_REJECTED', 'HOD Rejected'),
        ('PRINCIPAL_APPROVED', 'Principal Approved'),
        ('PRINCIPAL_REJECTED', 'Principal Rejected'),
    )

    MODE_CHOICES = (
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
    )

    name = me.StringField(max_length=200, required=True)
    coordinator = me.ReferenceField(CustomUser, required=True)
    department = me.StringField(max_length=10)
    event_name = me.StringField(max_length=200, required=True)
    about = me.StringField()
    title = me.StringField(max_length=200)
    date = me.DateField()
    time = me.StringField(max_length=10)
    expected_attendees = me.IntField(min_value=0)
    mode = me.StringField(max_length=10, choices=[c[0] for c in MODE_CHOICES])
    venue = me.StringField(max_length=200, null=True)
    meeting_link = me.StringField(max_length=500, null=True)

    budget = me.DecimalField(min_value=0)
    registration_fee = me.DecimalField(min_value=0)
    refreshment = me.DecimalField(min_value=0)
    renumeration = me.DecimalField(min_value=0)
    honorarium = me.DecimalField(min_value=0)
    other_requirements = me.StringField(default='')

    status = me.StringField(max_length=20, choices=[c[0] for c in STATUS_CHOICES], default='PENDING')
    hod_approval_date = me.DateTimeField(null=True)
    principal_approval_date = me.DateTimeField(null=True)
    event_id = me.StringField(max_length=50, unique=True)
    created_at = me.DateTimeField()

    meta = {
        'collection': 'events',
        'indexes': ['status', 'department', 'event_id', 'coordinator'],
        'ordering': ['-created_at'],
    }

    def __str__(self):
        return f"{self.event_name} - {self.department}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_mode_display(self):
        return dict(self.MODE_CHOICES).get(self.mode, self.mode)

    def get_department_display(self):
        return dict(CustomUser.DEPARTMENT_CHOICES).get(self.department, self.department or '')

    def get_department_display_name(self):
        return dict(CustomUser.DEPARTMENT_CHOICES).get(self.department, self.department or '')

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class EventSchedule(me.Document):
    event = me.ReferenceField(Event, required=True)
    session_name = me.StringField(max_length=200)
    start_time = me.StringField(max_length=10)
    end_time = me.StringField(max_length=10)

    meta = {'collection': 'event_schedules'}

    def __str__(self):
        return f"{self.event.event_name} - {self.session_name}"


class EventRegistration(me.Document):
    event = me.ReferenceField(Event, required=True)
    student = me.ReferenceField(CustomUser, required=True)
    registration_date = me.DateTimeField()
    certificate_generated = me.BooleanField(default=False)
    certificate_generated_date = me.DateTimeField(null=True)
    certificate_url = me.StringField(null=True)

    meta = {
        'collection': 'event_registrations',
        'indexes': [
            {'fields': ['event', 'student'], 'unique': True},
        ],
    }

    def __str__(self):
        return f"{self.student.username} - {self.event.event_name}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.registration_date:
            self.registration_date = timezone.now()
        super().save(*args, **kwargs)


class EventFeedback(me.Document):
    event = me.ReferenceField(Event, required=True)
    student = me.ReferenceField(CustomUser, required=True)
    feedback_text = me.StringField()
    rating = me.IntField(min_value=1, max_value=5)
    submitted_date = me.DateTimeField()

    meta = {
        'collection': 'event_feedbacks',
        'indexes': [
            {'fields': ['event', 'student'], 'unique': True},
        ],
    }

    def __str__(self):
        return f"{self.student.username}'s feedback for {self.event.event_name}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.submitted_date:
            self.submitted_date = timezone.now()
        super().save(*args, **kwargs)


class EventMaterial(me.Document):
    event = me.ReferenceField(Event, required=True)
    title = me.StringField(max_length=200)
    description = me.StringField(default='')
    file = me.StringField(max_length=500)
    uploaded_at = me.DateTimeField()

    meta = {'collection': 'event_materials'}

    def __str__(self):
        return f"{self.title} - {self.event.event_name}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.uploaded_at:
            self.uploaded_at = timezone.now()
        super().save(*args, **kwargs)


class EventAssessment(me.Document):
    event = me.ReferenceField(Event, required=True)
    title = me.StringField(max_length=200)
    description = me.StringField()
    due_date = me.DateTimeField()
    total_marks = me.IntField(default=100)
    created_at = me.DateTimeField()
    is_ai_generated = me.BooleanField(default=False)
    passing_score = me.IntField(default=3)

    meta = {
        'collection': 'event_assessments',
        'indexes': ['event'],
    }

    def __str__(self):
        return f"{self.title} - {self.event.event_name}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class Question(me.Document):
    QUESTION_TYPE_CHOICES = (
        ('MCQ', 'Multiple Choice Question'),
        ('MSQ', 'Multiple Select Question'),
        ('NAT', 'Numerical Answer Type'),
    )

    assessment = me.ReferenceField(EventAssessment, required=True)
    question_text = me.StringField()
    question_type = me.StringField(max_length=3, choices=[c[0] for c in QUESTION_TYPE_CHOICES])
    marks = me.IntField(default=1, min_value=0)

    meta = {
        'collection': 'questions',
        'indexes': ['assessment'],
    }

    def __str__(self):
        return f"{self.question_text[:30]}..."


class QuestionOption(me.Document):
    question = me.ReferenceField(Question, required=True)
    option_text = me.StringField(max_length=255)
    is_correct = me.BooleanField(default=False)

    meta = {
        'collection': 'question_options',
        'indexes': ['question'],
    }

    def __str__(self):
        return self.option_text


class NumericalAnswer(me.Document):
    question = me.ReferenceField(Question, required=True, unique=True)
    correct_answer = me.FloatField()
    tolerance = me.FloatField(default=0.0)

    meta = {'collection': 'numerical_answers'}

    def __str__(self):
        return f"{self.correct_answer} (±{self.tolerance})"


class AssessmentSubmission(me.Document):
    assessment = me.ReferenceField(EventAssessment, required=True)
    student = me.ReferenceField(CustomUser, required=True)
    submission_file = me.StringField(null=True)
    submitted_at = me.DateTimeField()
    score = me.IntField(null=True)
    is_ai_graded = me.BooleanField(default=False)

    meta = {
        'collection': 'assessment_submissions',
        'indexes': [
            {'fields': ['assessment', 'student'], 'unique': True},
        ],
    }

    def __str__(self):
        return f"{self.student.username}'s submission for {self.assessment.title}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.submitted_at:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)


class StudentAnswer(me.Document):
    submission = me.ReferenceField(AssessmentSubmission, required=True)
    question = me.ReferenceField(Question, required=True)
    selected_option_ids = me.ListField(me.ObjectIdField(), default=list)
    numerical_value = me.FloatField(null=True)
    is_correct = me.BooleanField(default=False)

    meta = {
        'collection': 'student_answers',
        'indexes': [
            {'fields': ['submission', 'question'], 'unique': True},
        ],
    }

    def get_selected_options(self):
        return QuestionOption.objects(id__in=self.selected_option_ids)

    def __str__(self):
        return f"Answer for {self.question}"
