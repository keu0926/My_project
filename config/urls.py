from django.contrib import admin
from django.urls import path
from main import views  # 우리가 만든 main 앱의 home 함수를 가져옵니다.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  
    path('class/retake/', views.class_retake, name='class_retake'),
    path('intro/greeting/', views.intro_greeting, name='intro_greeting'),
    path('intro/teachers/', views.intro_teachers, name='intro_teachers'),
    path('intro/results/', views.intro_results, name='intro_results'),
    path('intro/facility/', views.intro_facility, name='intro_facility'),
    path('intro/location/', views.intro_location, name='intro_location'),
    path('system/x10/', views.system_x10, name='system_x10'),
    path('system/life/', views.system_life, name='system_life'),
    path('booking/', views.consult_view, name='booking'),
    path('consult/', views.consult_view, name='consult'),
    path("notice/", views.notice_list, name="notice_list"),
    path("notice/<int:pk>/", views.notice_detail, name="notice_detail"),
]
