from django.urls import path
from . import views

app_name = 'academy_admin'

urlpatterns = [
    path('', views.dashboard_redirect_view, name='home'),
    path('schedule/', views.manage_schedule_view, name='schedule_manage'),
    path('students/', views.student_enroll_view, name='student_enroll'),
]