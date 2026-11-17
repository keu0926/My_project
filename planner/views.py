from functools import wraps
from django.shortcuts import render, redirect
from django.utils import timezone


def planner_permission_required(view_func):
    """로그인 여부 및 관리자의 '학습플래너 사용 권한' 승인 여부를 검사하는 보안 데코레이터"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 1. 비로그인 사용자는 로그인 페이지로 이동 (로그인 후 다시 플래너로 돌아오도록 next 파라미터 전달)
        if not request.user.is_authenticated:
            return redirect(f"/login/?next={request.path}")

        # 2. 최고관리자 및 스태프(원장님/선생님)는 무조건 통과
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # 3. 일반 회원(학생/학부모)은 프로필의 can_use_planner 권한이 True인지 확인
        profile = getattr(request.user, 'profile', None)
        if profile and profile.can_use_planner:
            return view_func(request, *args, **kwargs)

        # 4. 권한이 없는 회원은 접근 제한 안내 화면 표시
        return render(request, 'planner/access_denied.html', status=403)

    return _wrapped_view


@planner_permission_required
def dashboard_view(request):
    """플래너 메인 대시보드 (기존 홈페이지 메뉴와 완전히 분리된 독립 화면)"""
    profile = getattr(request.user, 'profile', None)
    user_display_name = profile.name if profile else (request.user.first_name or request.user.username)

    context = {
        'user_display_name': user_display_name,
        'profile': profile,
        'today': timezone.localdate(),
    }
    return render(request, 'planner/dashboard.html', context)