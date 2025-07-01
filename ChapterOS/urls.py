from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.users.urls")),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing_page"),
    path("recruitments/", include("apps.recruitments.urls")),
    path("form_builder/", include("apps.form_builder.urls")),
    path("calendar/", include("apps.calendar_app.urls")),
]

handler400 = 'ChapterOS.views.handler400'
handler403 = 'ChapterOS.views.handler403'
handler404 = 'ChapterOS.views.handler404'
handler500 = 'ChapterOS.views.handler500'