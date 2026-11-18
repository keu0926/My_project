from django.conf import settings
from django.db import models
from django.utils import timezone


class DailyPlanner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_planners',
        verbose_name='학생'
    )
    date = models.DateField(default=timezone.localdate, verbose_name='날짜')

    todays_point = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='오늘의 핵심 목표'
    )

    timetable_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='타임테이블 기록'
    )

    todo_data = models.JSONField(
        default=list,
        blank=True,
        verbose_name='투두리스트 기록'
    )

    timer_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='과목별 순공 시간(초)'
    )

    total_study_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name='총 순공 시간(초)'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최근 저장 시각')

    class Meta:
        verbose_name = '일일 학습 플래너'
        verbose_name_plural = '일일 학습 플래너 목록'
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_user_daily_planner')
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date} 플래너"
