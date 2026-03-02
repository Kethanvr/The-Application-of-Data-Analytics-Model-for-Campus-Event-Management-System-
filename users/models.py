from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('EVENT_COORDINATOR', 'Event Coordinator'),
        ('HOD', 'Head of Department'),
        ('PRINCIPAL', 'Principal'),
    ]

    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science & Engineering'),
        ('ISE', 'Information Science & Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('MBA', 'Master of Business Administration'),
        ('MCA', 'Master of Computer Applications'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    usn = models.CharField(max_length=20, blank=True, null=True, verbose_name='USN')

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_department_display_name(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)
