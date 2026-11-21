from django.urls import path
from . import views

app_name = 'total_schedule'

urlpatterns = [
    path('manage/', views.manage_schedule_view, name='manage'),
    path('students/', views.student_enroll_view, name='student_enroll'),
]