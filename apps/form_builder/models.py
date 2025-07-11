from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Form(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forms')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Section(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} (Form: {self.form.title})"

    class Meta:
        ordering = ['order']

class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('textarea', 'Text Area'),
        ('radio', 'Radio'),
        ('checkbox', 'Checkbox'),
        ('dropdown', 'Dropdown'),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    label = models.CharField(max_length=255)
    placeholder = models.CharField(max_length=255, blank=True, null=True)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    regex_validation_rules = models.TextField(blank=True, null=True, help_text="Enter a regex pattern for validation.")

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['order']

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.label

    def clean(self):
        if self.question.type not in ['radio', 'checkbox', 'dropdown']:
            raise ValidationError("Options can only be added to 'Radio', 'Checkbox', or 'Dropdown' question types.")

    class Meta:
        ordering = ['order']

class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    response_value = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to '{self.question.label}' in form '{self.form.title}'"