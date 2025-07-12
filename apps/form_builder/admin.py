from django.contrib import admin
from .models import (
    Form, Question, QuestionOption, GridRow, GridColumn,
    QuestionCondition, Submission, Answer, GridAnswer
)

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    ordering = ('display_order',)

class GridRowInline(admin.TabularInline):
    model = GridRow
    extra = 1
    ordering = ('display_order',)

class GridColumnInline(admin.TabularInline):
    model = GridColumn
    extra = 1
    ordering = ('display_order',)

class QuestionConditionInline(admin.StackedInline):
    model = QuestionCondition
    fk_name = 'question'
    extra = 0

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    ordering = ('display_order',)
    show_change_link = True
    inlines = [QuestionOptionInline, GridRowInline, GridColumnInline]

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'is_approved', 'created_at')
    list_filter = ('is_active', 'is_approved', 'user')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'user')
        }),
        ('Status & Approval', {
            'fields': ('is_active', 'is_approved')
        }),
        ('Configuration', {
            'fields': ('deadline', 'confirmation_message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        
        is_chair = request.user.groups.filter(name='Chair').exists()
        
        if not request.user.is_superuser and not is_chair:
            return list(readonly_fields) + ['is_approved']
        
        return readonly_fields

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'form', 'type', 'display_order', 'is_required')
    list_filter = ('form', 'type', 'is_required')
    search_fields = ('question_text',)
    inlines = [QuestionOptionInline, GridRowInline, GridColumnInline, QuestionConditionInline]

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('form', 'respondent_email', 'submitted_at')
    list_filter = ('form',)
    date_hierarchy = 'submitted_at'
    inlines = [AnswerInline]

admin.site.register(QuestionOption)
admin.site.register(GridRow)
admin.site.register(GridColumn)
admin.site.register(Answer)
admin.site.register(GridAnswer)
admin.site.register(QuestionCondition)