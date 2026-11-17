from django.db import models

class Notice(models.Model):
    title = models.CharField("제목", max_length=200)
    category = models.CharField(
        "분류",
        max_length=20,
        choices=[
            ("학사일정", "학사일정"),
            ("생활안내", "생활안내"),
            ("입시정보", "입시정보"),
            ("일반공지", "일반공지"),
        ],
        default="일반공지",
    )
    content = models.TextField("내용")
    is_pinned = models.BooleanField("상단 중요 공지 고정", default=False)
    views = models.PositiveIntegerField("조회수", default=0)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "공지사항"
        verbose_name_plural = "공지사항 관리"
        # 중요 공지를 먼저 띄우고, 최신순으로 정렬
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title




from django.db import models
from django.contrib.auth.models import User


class MemberProfile(models.Model):
    ROLE_CHOICES = [
        ('student', '학생 회원'),
        ('parent', '학부모 회원'),
    ]
    LIVING_CHOICES = [
        ('commute', '통학 (자택)'),
        ('dorm', '학사 거주'),
        ('studio', '자취 (오피스텔·원룸)'),
    ]
    RELATION_CHOICES = [
        ('father', '부 (아버지)'),
        ('mother', '모 (어머니)'),
    ]
    COURSE_CHOICES = [
        ('retake', '재수종합반 (N수)'),
        ('ged', '검시대입반'),
        ('camp', '방학캠프반 (윈터/썸머)'),
        ('single', '영어·탐구·논술 단과'),
    ]

    # 1. 기본 계정 및 공통 정보 (Django 기본 User 모델과 1:1 연결)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='계정 아이디')
    user_role = models.CharField('회원 구분', max_length=10, choices=ROLE_CHOICES, default='student')
    name = models.CharField('성명', max_length=30)
    birthdate = models.DateField('생년월일', null=True, blank=True)
    phone = models.CharField('휴대폰 번호', max_length=15)
    region = models.CharField('거주 지역', max_length=30)

    # 2. 학생 회원 전용 정보
    high_school = models.CharField('출신 고등학교', max_length=50, blank=True)
    grade_status = models.CharField('지원 과정', max_length=20, choices=COURSE_CHOICES, blank=True)
    target_univ = models.CharField('목표 대학 및 학과', max_length=100, blank=True)

    # 등원 및 거주 형태 (통학 / 학사 / 자취)
    living_type = models.CharField('등원 및 거주 형태', max_length=15, choices=LIVING_CHOICES, blank=True)
    commute_method = models.CharField('주요 통학 수단', max_length=100, blank=True)
    commute_time = models.PositiveIntegerField('편도 통학 시간(분)', null=True, blank=True)
    dorm_name = models.CharField('이용 학사명', max_length=100, blank=True)
    studio_distance = models.PositiveIntegerField('자취방 이동 시간(분)', null=True, blank=True)

    # 학생의 학부모 연동 정보
    parent_name = models.CharField('학부모 성명', max_length=30, blank=True)
    parent_gender_relation = models.CharField('보호자 관계', max_length=10, choices=RELATION_CHOICES, blank=True)
    parent_phone = models.CharField('학부모 연락처', max_length=15, blank=True)

    # 3. 학부모 회원 전용 정보
    child_name = models.CharField('자녀 성명', max_length=30, blank=True)
    parent_self_relation = models.CharField('자녀와의 관계', max_length=10, choices=RELATION_CHOICES, blank=True)
    child_birthdate = models.DateField('자녀 생년월일', null=True, blank=True)
    child_phone = models.CharField('자녀 휴대폰 번호', max_length=15, blank=True)

    # 4. 약관 동의 여부 및 가입일
    agree_service = models.BooleanField('이용약관 동의', default=True)
    agree_privacy = models.BooleanField('개인정보 수집 동의', default=True)
    agree_report = models.BooleanField('알림톡 수신 동의', default=True)
    agree_marketing = models.BooleanField('마케팅 수신 동의(선택)', default=False)
    created_at = models.DateTimeField('가입일시', auto_now_add=True)

    # main/models.py 의 MemberProfile 클래스 내부 맨 아래에 추가
    can_use_planner = models.BooleanField("학습플래너 사용 권한", default=False)

    class Meta:
        verbose_name = '대치플투스 회원 프로필'
        verbose_name_plural = '대치플투스 회원 프로필 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_user_role_display()}] {self.name} ({self.user.username})"