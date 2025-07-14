from django.core.management.base import BaseCommand
from apps.events.models import AcademicYear

class Command(BaseCommand):
    help = 'Populates the AcademicYear table with initial data'

    def handle(self, *args, **kwargs):
        academic_years = [
            ('FY', 'First Year'),
            ('SY', 'Second Year'),
            ('TY', 'Third Year'),
            ('FR', 'Fourth Year'),
        ]
        for code, _ in academic_years:
            AcademicYear.objects.get_or_create(name=code)
            self.stdout.write(self.style.SUCCESS(f'Successfully created or verified academic year: {code}'))