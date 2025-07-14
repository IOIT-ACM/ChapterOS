from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Main Calendar View
    path('', views.calendar_view, name='calendar'),

    # API Endpoints
    path('api/events/', views.api_events, name='api_events'),
    path('api/categories/', views.api_event_categories, name='api_event_categories'),
    path('api/categories/bulk-add/', views.api_bulk_add_categories, name='api_bulk_add_categories'),
    path('api/statuses/', views.api_event_statuses, name='api_event_statuses'),
    path('api/event/<int:event_id>/history/', views.api_event_history, name='api_event_history'),

    # Event Actions (Modal form submissions)
    path('add/', views.add_event, name='add_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('bulk-upload/', views.bulk_upload_events, name='bulk_upload'),
    path('download-sample/', views.download_sample_csv, name='download_sample_csv'),
    
    # Standalone event detail page
    path('<int:event_id>/', views.event_detail_view, name='event_detail'),
]