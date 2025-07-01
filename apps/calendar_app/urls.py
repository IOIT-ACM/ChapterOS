from django.urls import path
from . import views

app_name = "calendar_app"

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('events/', views.calendar_events, name='calendar_events'),
]
