from django.urls import path
from planner import views

app_name = 'planner'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('save/', views.save_daily_planner, name='save_daily_planner'),
]