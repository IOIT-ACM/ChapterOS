from django.contrib import admin, messages
from .models import Event, EventCategory, EventParticipant, EventNotification, EventHistory

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)

@admin.action(description='Mark selected events as Public')
def make_public(modeladmin, request, queryset):
    queryset.update(privacy='PUBLIC')
    modeladmin.message_user(request, f"{queryset.count()} events were successfully marked as public.", messages.SUCCESS)

@admin.action(description='Mark selected events as Private')
def make_private(modeladmin, request, queryset):
    queryset.update(privacy='PRIVATE')
    modeladmin.message_user(request, f"{queryset.count()} events were successfully marked as private.", messages.SUCCESS)

@admin.action(description='Change status to Planned')
def change_status_planned(modeladmin, request, queryset):
    queryset.update(status='PLANNED')
    modeladmin.message_user(request, f"{queryset.count()} events had their status changed to Planned.", messages.SUCCESS)

@admin.action(description='Change status to In Progress')
def change_status_in_progress(modeladmin, request, queryset):
    queryset.update(status='IN_PROGRESS')
    modeladmin.message_user(request, f"{queryset.count()} events had their status changed to In Progress.", messages.SUCCESS)

@admin.action(description='Change status to Completed')
def change_status_completed(modeladmin, request, queryset):
    queryset.update(status='COMPLETED')
    modeladmin.message_user(request, f"{queryset.count()} events had their status changed to Completed.", messages.SUCCESS)

@admin.action(description='Change status to Cancelled')
def change_status_cancelled(modeladmin, request, queryset):
    queryset.update(status='CANCELLED')
    modeladmin.message_user(request, f"{queryset.count()} events had their status changed to Cancelled.", messages.SUCCESS)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'category', 'status', 'privacy', 'created_by')
    list_filter = ('status', 'privacy', 'category', 'start_date')
    search_fields = ('title', 'description', 'location')
    raw_id_fields = ('created_by', 'approved_by', 'parent_event')
    date_hierarchy = 'start_date'
    actions = [
        'delete_selected',
        make_public,
        make_private,
        change_status_planned,
        change_status_in_progress,
        change_status_completed,
        change_status_cancelled,
    ]

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'email', 'attendance_status', 'registration_date')
    list_filter = ('attendance_status', 'event')
    search_fields = ('name', 'email', 'roll_no')
    raw_id_fields = ('event',)

@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'type', 'scheduled_time', 'is_sent', 'delivery_method')
    list_filter = ('is_sent', 'type', 'delivery_method')
    search_fields = ('message', 'user__username', 'event__title')
    raw_id_fields = ('event', 'user')

@admin.register(EventHistory)
class EventHistoryAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'action', 'field_changed', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('event__title', 'user__username', 'field_changed')
    raw_id_fields = ('event', 'user')
