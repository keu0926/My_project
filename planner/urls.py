from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('stats/', views.stats_view, name='stats'), # ★ 통계 페이지 경로 추가
]