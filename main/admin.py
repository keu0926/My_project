from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Notice, MemberProfile


# 1. 공지사항 관리
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "title", "is_pinned", "views", "created_at")
    list_display_links = ("title",)
    list_editable = ("is_pinned",)  # 목록에서 바로 상단 고정 체크 가능
    list_filter = ("category", "is_pinned")
    search_fields = ("title", "content")


# 2. 단독 메뉴로 '대치플투스 회원 프로필 목록' 표시 (플래너 권한 즉시 체크 가능)
@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'user_role', 'can_use_planner', 'phone', 'region',
        'grade_status', 'living_type', 'parent_phone', 'child_name', 'created_at'
    )
    list_display_links = ('name', 'user')
    list_editable = ('can_use_planner',)  # ★ 목록에서 체크박스로 플래너 권한 즉시 부여/해제
    list_filter = ('can_use_planner', 'user_role', 'region', 'grade_status', 'living_type', 'agree_marketing')
    search_fields = ('name', 'user__username', 'phone', 'high_school', 'parent_name', 'parent_phone', 'child_name')


# 3. 기본 '사용자(Users)' 상세 페이지 하단에도 프로필 정보가 같이 뜨도록 연결
class MemberProfileInline(admin.StackedInline):
    model = MemberProfile
    can_delete = False
    verbose_name_plural = '대치플투스 학생/학부모 상세 프로필'


class UserAdmin(BaseUserAdmin):
    inlines = (MemberProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)