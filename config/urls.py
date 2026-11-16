from django.contrib import admin
from django.urls import path
from main import views  # 우리가 만든 main 앱의 home 함수를 가져옵니다.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  
    path('sub-class-1/', views.sub_class_1, name='sub_class_1'),
    path('sub-intro-1/', views.sub_intro_1, name='sub_intro_1'),
    path('sub-intro-2/', views.sub_intro_2, name='sub_intro_2'),
    path('sub-intro-3/', views.sub_intro_3, name='sub_intro_3'),
    path('sub-intro-4/', views.sub_intro_4, name='sub_intro_4'),
    path('sub-intro-5/', views.sub_intro_5, name='sub_intro_5'),
    path('sub-system-1/', views.sub_system_1, name='sub_system_1'),
    path('sub-system-2/', views.sub_system_2, name='sub_system_2'),
    path('sub-booking/', views.consult_view, name='sub_booking'),
    path('consult/', views.consult_view, name='consult'),
    path("notice/", views.notice_list, name="notice_list"),
    path("notice/<int:pk>/", views.notice_detail, name="notice_detail"),
]
