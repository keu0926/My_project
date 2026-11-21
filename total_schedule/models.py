from django.conf import settings
from django.db import models


class ScheduleSeason(models.Model):
    """시즌별 학원 토탈스케줄"""
    name = models.CharField(max_length=100, verbose_name='시즌명')
    is_active = models.BooleanField(default=False, verbose_name='현재 적용 시즌')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '스케줄 시즌'
        verbose_name_plural = '스케줄 시즌 목록'
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"{self.name} {'(적용중)' if self.is_active else ''}"


class PeriodConfig(models.Model):
    """시즌별 교시 및 식사/특수 시간 유동 설정"""
    season = models.ForeignKey(ScheduleSeason, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=50, verbose_name='교시/구간명')  # 예: '1교시', '점심 시간', '클리닉'
    is_break = models.BooleanField(default=False, verbose_name='식사/휴식 구간 여부')
    order = models.PositiveSmallIntegerField(default=1, verbose_name='정렬 순서')
    start_time = models.TimeField(verbose_name='시작 시각')
    end_time = models.TimeField(verbose_name='종료 시각')

    class Meta:
        verbose_name = '교시 시간 설정'
        verbose_name_plural = '교시 시간 설정 목록'
        ordering = ['order', 'start_time']

    @property
    def duration_minutes(self):
        start_min = self.start_time.hour * 60 + self.start_time.minute
        end_min = self.end_time.hour * 60 + self.end_time.minute
        return max(0, end_min - start_min)

    def __str__(self):
        return f"[{self.season.name}] {self.name} ({self.start_time:%H:%M}~{self.end_time:%H:%M})"


class ClassSlot(models.Model):
    """학원 토탈스케줄 개별 수업 블록 (동일 요일·교시에 최대 10명 강사 배정 가능)"""
    DAY_CHOICES = [
        (0, '월요일'), (1, '화요일'), (2, '수요일'), (3, '목요일'),
        (4, '금요일'), (5, '토요일'), (6, '일요일'),
    ]
    SUBJECT_CHOICES = [
        ('국어', '국어'), ('수학', '수학'), ('영어', '영어'),
        ('과탐', '과탐'), ('사탐', '사탐'), ('비교과', '비교과/모의고사/질의응답'),
    ]
    season = models.ForeignKey(ScheduleSeason, on_delete=models.CASCADE, related_name='class_slots')
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES, verbose_name='요일')
    period = models.ForeignKey(PeriodConfig, on_delete=models.CASCADE, related_name='slots')

    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name='과목')
    teacher_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ts_teaching_slots'
    )
    teacher_name = models.CharField(max_length=50, blank=True, default='', verbose_name='강사명')
    class_name = models.CharField(max_length=100, verbose_name='반명/활동명')
    is_merged = models.BooleanField(default=False, verbose_name='합반 여부')

    class Meta:
        verbose_name = '토탈스케줄 수업 블록'
        verbose_name_plural = '토탈스케줄 수업 블록 목록'
        ordering = ['day_of_week', 'period__order', 'id']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.period.get_code_display()} - {self.subject} {self.teacher_name} {self.class_name}"


class StudentEnrollment(models.Model):
    """학생 개인별 수강 반 배정"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ts_enrollments')
    season = models.ForeignKey(ScheduleSeason, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.CharField(max_length=20, verbose_name='과목')
    teacher_name = models.CharField(max_length=50, blank=True, default='', verbose_name='강사명')
    class_name = models.CharField(max_length=100, verbose_name='반명/활동명')

    class Meta:
        verbose_name = '학생 수강 반 배정'
        verbose_name_plural = '학생 수강 반 배정 목록'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'season', 'subject', 'teacher_name', 'class_name'],
                name='ts_unique_student_class_enrollment'
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.teacher_name} {self.class_name})"


class ClassLessonLog(models.Model):
    """강사가 작성하는 주차별 수업 내용 및 과제"""
    season = models.ForeignKey(ScheduleSeason, on_delete=models.CASCADE)
    subject = models.CharField(max_length=20, verbose_name='과목')
    teacher_name = models.CharField(max_length=50, blank=True, default='', verbose_name='강사명')
    class_name = models.CharField(max_length=100, verbose_name='반명')
    lesson_date = models.DateField(verbose_name='수업 날짜')
    content = models.TextField(blank=True, default='', verbose_name='수업 내용')
    homework = models.TextField(blank=True, default='', verbose_name='과제')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '수업 일지 및 과제'
        verbose_name_plural = '수업 일지 및 과제 목록'
        ordering = ['-lesson_date']