from django.contrib import admin
from .models import (
    ScheduleSeason,
    PeriodConfig,
    ClassSlot,
    StudentEnrollment,
    ClassLessonLog,
)


@admin.register(ScheduleSeason)
class ScheduleSeasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(PeriodConfig)
class PeriodConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'season', 'order', 'name', 'start_time', 'end_time', 'is_break')
    list_filter = ('season', 'is_break')
    ordering = ('season', 'order')


@admin.register(ClassSlot)
class ClassSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'season', 'day_of_week', 'period', 'subject', 'teacher_name', 'class_name', 'is_merged')
    list_filter = ('season', 'day_of_week', 'subject', 'is_merged')
    search_fields = ('teacher_name', 'class_name')


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'season', 'subject', 'teacher_name', 'class_name')
    list_filter = ('season', 'subject')
    search_fields = ('student__username', 'student__first_name', 'teacher_name', 'class_name')


@admin.register(ClassLessonLog)
class ClassLessonLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'season', 'lesson_date', 'subject', 'teacher_name', 'class_name')
    list_filter = ('season', 'subject', 'lesson_date')
    search_fields = ('teacher_name', 'class_name', 'content', 'homework')