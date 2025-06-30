from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing_page"),
    path("recruitments/", include("apps.recruitments.urls")),
    path("form_builder/", include("apps.form_builder.urls")),
]
