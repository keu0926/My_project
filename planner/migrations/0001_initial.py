import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPlanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.localdate, verbose_name='날짜')),
                ('todays_point', models.CharField(blank=True, default='', max_length=255, verbose_name='오늘의 핵심 목표')),
                ('timetable_data', models.JSONField(blank=True, default=dict, verbose_name='타임테이블 기록')),
                ('todo_data', models.JSONField(blank=True, default=list, verbose_name='투두리스트 기록')),
                ('timer_data', models.JSONField(blank=True, default=dict, verbose_name='과목별 순공 시간(초)')),
                ('total_study_seconds', models.PositiveIntegerField(default=0, verbose_name='총 순공 시간(초)')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='최근 저장 시각')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_planners', to=settings.AUTH_USER_MODEL, verbose_name='학생')),
            ],
            options={
                'verbose_name': '일일 학습 플래너',
                'verbose_name_plural': '일일 학습 플래너 목록',
                'ordering': ['-date'],
            },
        ),
        migrations.AddConstraint(
            model_name='dailyplanner',
            constraint=models.UniqueConstraint(fields=('user', 'date'), name='unique_user_daily_planner'),
        ),
    ]
