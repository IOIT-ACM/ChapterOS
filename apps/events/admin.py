from django.contrib import admin
from .models import Event, EventCategory, EventParticipant, EventNotification, EventHistory

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'category', 'status', 'created_by', 'is_recurring')
    list_filter = ('status', 'is_recurring', 'category', 'start_date')
    search_fields = ('title', 'description', 'location')
    raw_id_fields = ('created_by', 'approved_by', 'parent_event')
    date_hierarchy = 'start_date'

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