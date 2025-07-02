from django.urls import path
from . import views

app_name = 'recruitments'

urlpatterns = [
    path("", views.index, name="recruitments_index"),
    path("responses/acm-committee-2025-26/", views.recruitment_responses_view, name="recruitment_responses"),
    path("api/responses/acm-committee-2025-26/", views.recruitment_data_api, name="recruitment_data_api"),
]