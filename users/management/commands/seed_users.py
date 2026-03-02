"""
Management command: python manage.py seed_users

Creates the default admin (Principal) and demo student accounts in MongoDB.
Safe to run multiple times — skips existing usernames.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed initial demo users into MongoDB'

    def handle(self, *args, **options):
        from users.models import CustomUser

        users_to_create = [
            {
                'username': 'admin',
                'password': 'Admin@123',
                'email': 'admin@cmrit.ac.in',
                'first_name': 'Admin',
                'last_name': 'Principal',
                'role': 'PRINCIPAL',
                'department': 'CSE',
                'is_staff': True,
            },
            {
                'username': 'testuser1',
                'password': 'password123',
                'email': 'student@cmrit.ac.in',
                'first_name': 'Test',
                'last_name': 'Student',
                'role': 'STUDENT',
                'department': 'CSE',
            },
        ]

        for u in users_to_create:
            if CustomUser.objects(username=u['username']).first():
                self.stdout.write(f"  skip  {u['username']} (already exists)")
                continue
            pwd = u.pop('password')
            user = CustomUser.create_user(password=pwd, **u)
            self.stdout.write(self.style.SUCCESS(f"  created {user.username} ({user.role})"))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
