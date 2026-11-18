from django.contrib import admin
from planner.models import DailyPlanner


@admin.register(DailyPlanner)
class DailyPlannerAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'todays_point', 'total_study_seconds', 'updated_at')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__first_name', 'todays_point')
    ordering = ('-date', '-updated_at')