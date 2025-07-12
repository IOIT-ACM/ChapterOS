from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Form(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forms')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(blank=True, null=True)
    confirmation_message = models.TextField(blank=True, null=True, default="Thank you for your submission.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            queryset = Form.objects.filter(slug__startswith=self.slug).exclude(id=self.id)
            counter = 1
            while Form.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Question(models.Model):
    QUESTION_TYPES = [
        ('short_answer', 'Short Answer'),
        ('paragraph', 'Paragraph'),
        ('multiple_choice', 'Multiple Choice'),
        ('multiple_choice', 'Single Choice'),
        ('dropdown', 'Dropdown'),
        ('file_upload', 'File Upload'),
        ('linear_scale', 'Linear Scale'),
        ('rating', 'Rating'),
        ('multiple_choice_grid', 'Multiple Choice Grid'),
        ('date', 'Date'),
        ('time', 'Time'),
    ]

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    identifier = models.CharField(max_length=100, blank=True)
    question_text = models.CharField(max_length=500)
    description_text = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(default=dict, blank=True)
    question_config = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if not self.identifier:
            base_identifier = slugify(self.question_text) or "question"
            base_identifier = base_identifier[:95]
            
            counter = 1
            identifier = base_identifier
            while Question.objects.filter(form=self.form, identifier=identifier).exclude(pk=self.pk).exists():
                identifier = f"{base_identifier}-{counter}"
                counter += 1
            self.identifier = identifier
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text

    class Meta:
        ordering = ['display_order']
        unique_together = ('form', 'identifier')

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_other_option = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['display_order']

class GridRow(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='grid_rows')
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['display_order']

class GridColumn(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='grid_columns')
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['display_order']

class QuestionCondition(models.Model):
    CONDITION_TYPES = [
        ('show_if', 'Show If'),
        ('hide_if', 'Hide If'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='conditions')
    depends_on_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='triggers')
    trigger_value = models.JSONField()
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)

    def __str__(self):
        return f"Condition for '{self.question.question_text}'"

class Submission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    respondent_email = models.EmailField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission for {self.form.title} at {self.submitted_at}"

class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_value = models.TextField(blank=True)
    other_text = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Answer to '{self.question.question_text}'"

class GridAnswer(models.Model):
    answer = models.OneToOneField(Answer, on_delete=models.CASCADE, related_name='grid_answer')
    grid_row = models.ForeignKey(GridRow, on_delete=models.CASCADE)
    grid_column = models.ForeignKey(GridColumn, on_delete=models.CASCADE)

    def __str__(self):
        return f"Grid answer for row '{self.grid_row.label}'"