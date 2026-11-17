from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # 1. 학원 소개 (Intro)
    path('intro/greeting/', views.intro_greeting, name='intro_greeting'),   # 학원 소개
    path('intro/teachers/', views.intro_teachers, name='intro_teachers'),   # 코칭 스텝
    path('intro/facility/', views.intro_facility, name='intro_facility'),   # 학원 시설
    path('intro/meal/', views.intro_meal, name='intro_meal'),               # ★ 신규: 급식 예고
    path('intro/location/', views.intro_location, name='intro_location'),   # 오시는 길

    # 2. 학습 안내 (System)
    path('system/x10/', views.system_x10, name='system_x10'),               # 학습 관리
    path('system/life/', views.system_life, name='system_life'),            # 생활 관리
    path('system/voca/', views.system_voca, name='system_voca'),            # ★ 신규: 단어 시험
    path('system/mock/', views.system_mock, name='system_mock'),            # ★ 신규: 주간 모고

    # 3. 모집 요강 (Class)
    path('class/retake/', views.class_retake, name='class_retake'),         # 재수종합
    path('class/ged/', views.class_ged, name='class_ged'),                  # ★ 신규: 검시대입
    path('class/camp/', views.class_camp, name='class_camp'),               # ★ 신규: 방학캠프
    path('class/english/', views.class_english, name='class_english'),      # ★ 신규: 영어단과
    path('class/inquiry/', views.class_inquiry, name='class_inquiry'),      # ★ 신규: 탐구단과
    path('class/essay/', views.class_essay, name='class_essay'),            # ★ 신규: 대입논술

    # 4. 상담실 (Consult & Notice)
    path('booking/', views.consult_view, name='booking'),                   # 상담 예약
    path('consult/', views.consult_view, name='consult'),                   # 상담 예약 (보조 경로)
    path('notice/', views.notice_list, name='notice_list'),                 # 공지 사항 (목록)
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),    # 공지 사항 (상세)
    path('guide/', views.guide_info, name='guide_info'),                    # ★ 신규: 안내 사항

    # 5. 입시 실적 (Results)
    path('intro/results/', views.intro_results, name='intro_results'),      # 명예의 전당
]