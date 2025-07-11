from django.urls import path, include
from . import views

app_name = 'form_builder'

api_urlpatterns = [
    path('forms/<int:pk>/schema/', views.FormSchemaAPIView.as_view(), name='api_form_schema'),
    path('sections/', views.SectionListCreateAPIView.as_view(), name='api_section_list_create'),
    path('sections/<int:pk>/', views.SectionRetrieveUpdateDestroyAPIView.as_view(), name='api_section_detail'),
    path('questions/', views.QuestionListCreateAPIView.as_view(), name='api_question_list_create'),
    path('questions/<int:pk>/', views.QuestionRetrieveUpdateDestroyAPIView.as_view(), name='api_question_detail'),
    path('options/', views.QuestionOptionListCreateAPIView.as_view(), name='api_option_list_create'),
    path('options/<int:pk>/', views.QuestionOptionRetrieveUpdateDestroyAPIView.as_view(), name='api_option_detail'),
]

urlpatterns = [
    path('', views.FormListView.as_view(), name='form_list'),
    path('create/', views.FormCreateView.as_view(), name='form_create'),
    path('<int:pk>/build/', views.form_builder_view, name='form_build'),
    path('<int:pk>/delete/', views.FormDeleteView.as_view(), name='form_delete'),
    path('api/', include(api_urlpatterns)),
]