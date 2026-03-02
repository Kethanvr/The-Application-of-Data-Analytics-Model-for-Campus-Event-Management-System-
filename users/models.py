import mongoengine as me
from django.contrib.auth.hashers import make_password, check_password as django_check_password


class CustomUser(me.Document):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('EVENT_COORDINATOR', 'Event Coordinator'),
        ('HOD', 'Head of Department'),
        ('PRINCIPAL', 'Principal'),
    )

    DEPARTMENT_CHOICES = (
        ('CSE', 'Computer Science & Engineering'),
        ('ISE', 'Information Science & Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('MBA', 'Master of Business Administration'),
        ('MCA', 'Master of Computer Applications'),
    )

    username = me.StringField(max_length=150, unique=True, required=True)
    email = me.EmailField(max_length=254, default='')
    first_name = me.StringField(max_length=150, default='')
    last_name = me.StringField(max_length=150, default='')
    password = me.StringField(required=True)
    role = me.StringField(max_length=20, choices=[c[0] for c in ROLE_CHOICES], default='STUDENT')
    department = me.StringField(max_length=10, choices=[c[0] for c in DEPARTMENT_CHOICES], null=True)
    phone_number = me.StringField(max_length=15, null=True)
    profile_picture = me.StringField(null=True)
    usn = me.StringField(max_length=20, null=True)
    is_active = me.BooleanField(default=True)
    is_staff = me.BooleanField(default=False)
    date_joined = me.DateTimeField()

    meta = {
        'collection': 'users',
        'indexes': ['username', 'email'],
    }

    # ── Django auth compatibility ──────────────────────────────────────────────
    is_anonymous = False
    is_authenticated = True

    @property
    def pk(self):
        return str(self.id)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.username

    def get_short_name(self):
        return self.first_name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

    def get_department_display_name(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)

    def get_department_display(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department or '')

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    # Needed for django.contrib.messages
    def _get_pk_val(self):
        return str(self.id)

    @classmethod
    def objects_filter(cls, **kwargs):
        return cls.objects(**kwargs)

    @classmethod
    def create_user(cls, username, password, email='', first_name='', last_name='',
                    role='STUDENT', department=None, **extra):
        from django.utils import timezone
        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department or None,
            date_joined=timezone.now(),
            **extra
        )
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_superuser(cls, username, password, email='', **extra):
        return cls.create_user(
            username=username,
            password=password,
            email=email,
            role='PRINCIPAL',
            is_staff=True,
            **extra
        )
