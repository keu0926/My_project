from django.contrib import admin
from .models import Notice

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "title", "is_pinned", "views", "created_at")
    list_display_links = ("title",)
    list_editable = ("is_pinned",)  # 목록에서 바로 상단 고정 체크 가능
    list_filter = ("category", "is_pinned")
    search_fields = ("title", "content")
