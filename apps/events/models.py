from django.db import models
from django.conf import settings
from django.db.models import Q

# module‐level constant so it's available for field choices and DB constraint
ACADEMIC_YEAR_CHOICES = [
    ('FY', 'First Year'),
    ('SY', 'Second Year'),
    ('TY', 'Third Year'),
    ('FR', 'Fourth Year'),
]

class EventCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    color = models.CharField(
        max_length=7,
        default='#FFFFFF',
        help_text="Hex color code, e.g., #RRGGBB"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Event Categories"


class AcademicYear(models.Model):
    """
    Defines exactly these four academic years.
    """
    name = models.CharField(
        max_length=2,
        choices=ACADEMIC_YEAR_CHOICES,
        unique=True,
        help_text="Select one of: FY, SY, TY, FR"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        constraints = [
            models.CheckConstraint(
                check=Q(name__in=[code for code, _ in ACADEMIC_YEAR_CHOICES]),
                name='valid_academic_year_name'
            )
        ]

    def __str__(self):
        return dict(ACADEMIC_YEAR_CHOICES)[self.name]


class Event(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    PRIVACY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_events'
    )
    parent_event = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_events'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='PUBLIC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    academic_years = models.ManyToManyField(
        AcademicYear,
        through='EventAcademicYear',
        related_name='events'
    )

    def __str__(self):
        return self.title


class EventAcademicYear(models.Model):
    """
    Junction table linking Events to one or more AcademicYears.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_year_links'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='event_year_links'
    )

    class Meta:
        unique_together = ('event', 'academic_year')
        verbose_name = "Event–Academic Year Link"
        verbose_name_plural = "Event–Academic Year Links"

    def __str__(self):
        return f"{self.event.title} ↔ {self.academic_year.name}"


class EventParticipant(models.Model):
    ATTENDANCE_STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('ATTENDED', 'Attended'),
        ('ABSENT', 'Absent'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=100, blank=True)
    roll_no = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20, blank=True)
    attendance_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='REGISTERED'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} for {self.event.title}"


class EventNotification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_notifications')
    type = models.CharField(max_length=50)
    message = models.TextField()
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_method = models.CharField(max_length=20, default='Email')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.event.title} to {self.user.username}"


class EventHistory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='history_logs')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_history_actions'
    )
    action = models.CharField(max_length=50)
    field_changed = models.CharField(max_length=100, blank=True, null=True)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Example Log Entries:
    # 1. Event Creation:
    #    - event: <Event object>
    #    - user: <User object>
    #    - action: "created"
    #    - field_changed: None
    #    - old_value: None
    #    - new_value: None
    #
    # 2. Field Update:
    #    - event: <Event object>
    #    - user: <User object>
    #    - action: "updated"
    #    - field_changed: "Title"
    #    - old_value: "Old Event Title"
    #    - new_value: "New Event Title"

    def __str__(self):
        return f"{self.action} on {self.event.title} by {self.user.username if self.user else 'System'}"
