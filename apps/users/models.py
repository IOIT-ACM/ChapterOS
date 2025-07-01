from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    ACADEMIC_YEAR_CHOICES = [
        ('', '---------'),
        ('First year', 'First year'),
        ('Second year', 'Second year'),
        ('Third year', 'Third year'),
        ('Fourth year', 'Fourth year'),
    ]

    TEAM_CHOICES = [
        ('', '---------'),
        ('Core', 'Core'),
        ('Tech', 'Tech'),
        ('Web', 'Web'),
        ('Doc', 'Doc'),
        ('Event Management', 'Event Management'),
        ('Media', 'Media'),
    ]

    BRANCH_CHOICES = [
        ('', '---------'),
        ('AI&D', 'AI & Data Science'),
        ('CS', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('ENTC', 'Electronics & Telecommunication'),
        ('ELEC', 'Electrical Engineering'),
        ('INSTRU', 'Instrumentation Engineering'),
    ]

    full_name = models.CharField(max_length=255, blank=True)
    mobile_number_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile_number = models.CharField(validators=[mobile_number_validator], max_length=17, blank=True)
    academic_year = models.CharField(max_length=20, choices=ACADEMIC_YEAR_CHOICES, blank=True)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, blank=True)
    team = models.CharField(max_length=50, choices=TEAM_CHOICES, blank=True)

    def __str__(self):
        return self.username