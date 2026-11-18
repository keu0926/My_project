from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # 1. 학원 소개
    path('intro/greeting/', views.intro_greeting, name='intro_greeting'),
    path('intro/teachers/', views.intro_teachers, name='intro_teachers'),
    path('intro/facility/', views.intro_facility, name='intro_facility'),
    path('intro/meal/', views.intro_meal, name='intro_meal'),
    path('intro/location/', views.intro_location, name='intro_location'),

    # 2. 학습 안내
    path('system/x10/', views.system_x10, name='system_x10'),
    path('system/life/', views.system_life, name='system_life'),
    path('system/voca/', views.system_voca, name='system_voca'),
    path('system/mock/', views.system_mock, name='system_mock'),

    # 3. 모집 요강
    path('class/retake/', views.class_retake, name='class_retake'),
    path('class/ged/', views.class_ged, name='class_ged'),
    path('class/camp/', views.class_camp, name='class_camp'),
    path('class/english/', views.class_english, name='class_english'),
    path('class/inquiry/', views.class_inquiry, name='class_inquiry'),
    path('class/essay/', views.class_essay, name='class_essay'),

    # 4. 상담실 및 공지
    path('booking/', views.consult_view, name='booking'),
    path('consult/', views.consult_view, name='consult'),
    path('notice/', views.notice_list, name='notice_list'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('guide/', views.guide_info, name='guide_info'),

    # 5. 입시 실적
    path('intro/results/', views.intro_results, name='intro_results'),

    # 6. 회원 가입 및 인증
    path('signup/', views.signup_view, name='signup'),
    path('api/check-username/', views.check_username_view, name='check_username'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 7. ★ 학습 플래너 (planner/urls.py로 완벽하게 위임)
    path('planner/', include('planner.urls')),
]