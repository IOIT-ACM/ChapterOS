from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="recruitments_index"),
]
