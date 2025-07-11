from django.contrib import admin
from .models import Form, Section, Question, QuestionOption, Response

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    ordering = ('order',)

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    ordering = ('order',)
    show_change_link = True

class SectionInline(admin.StackedInline):
    model = Section
    extra = 1
    ordering = ('order',)
    show_change_link = True

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'owner')
    search_fields = ('title', 'description')
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'form', 'order')
    list_filter = ('form',)
    search_fields = ('title',)
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('label', 'section', 'type', 'order', 'is_required')
    list_filter = ('section__form', 'type', 'is_required')
    search_fields = ('label',)
    inlines = [QuestionOptionInline]

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'form', 'submitted_at')
    list_filter = ('form', 'question')
    search_fields = ('response_value',)
    date_hierarchy = 'submitted_at'