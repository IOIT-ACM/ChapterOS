from django.urls import path, include
from . import views

app_name = 'form_builder'

api_urlpatterns = [
    path('forms/<slug:slug>/schema/', views.FormSchemaAPIView.as_view(), name='api_form_schema'),
    path('forms/public/<slug:slug>/schema/', views.PublicFormSchemaAPIView.as_view(), name='api_public_form_schema'),
    path('forms/<slug:slug>/reorder-questions/', views.ReorderQuestionsAPIView.as_view(), name='api_reorder_questions'),
    path('questions/', views.QuestionCreateAPIView.as_view(), name='api_question_create'),
    path('questions/<int:pk>/', views.QuestionRetrieveUpdateDestroyAPIView.as_view(), name='api_question_detail'),
    path('options/', views.QuestionOptionCreateAPIView.as_view(), name='api_option_create'),
    path('options/<int:pk>/', views.QuestionOptionRetrieveUpdateDestroyAPIView.as_view(), name='api_option_detail'),
]

urlpatterns = [
    path('', views.FormListView.as_view(), name='form_list'),
    path('create/', views.FormCreateView.as_view(), name='form_create'),
    path('<slug:slug>/build/', views.form_builder_view, name='form_build'),
    path('<slug:slug>/settings/', views.FormSettingsView.as_view(), name='form_settings'),
    path('<slug:slug>/delete/', views.FormDeleteView.as_view(), name='form_delete'),
    path('api/', include(api_urlpatterns)),
]