import json
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import DailyPlanner


def planner_permission_required(view_func):
    """로그인 여부 및 관리자의 '학습플래너 사용 권한' 승인 여부를 검사하는 보안 데코레이터.
    저장(POST, fetch) 요청에는 HTML 대신 JSON 오류를 돌려줘서 화면에서 안내 문구가 뜨게 합니다."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        is_save_request = request.method == 'POST'

        # 1. 비로그인 사용자는 로그인 페이지로 이동 (로그인 후 다시 플래너로 돌아오도록 next 파라미터 전달)
        if not request.user.is_authenticated:
            if is_save_request:
                return JsonResponse({'status': 'error', 'message': '로그인이 필요합니다.'}, status=401)
            return redirect(f"/login/?next={request.path}")

        # 2. 최고관리자 및 스태프(원장님/선생님)는 무조건 통과
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # 3. 일반 회원(학생/학부모)은 프로필의 can_use_planner 권한이 True인지 확인
        profile = getattr(request.user, 'profile', None)
        if profile and profile.can_use_planner:
            return view_func(request, *args, **kwargs)

        # 4. 권한이 없는 회원은 접근 제한
        if is_save_request:
            return JsonResponse({'status': 'error', 'message': '학습플래너 사용 권한이 없습니다.'}, status=403)
        return render(request, 'planner/access_denied.html', status=403)

    return _wrapped_view


def _json_for_script(data):
    """<script type="application/json"> 안에 안전하게 넣을 수 있는 JSON 문자열.
    '<', '>', '&' 를 이스케이프해서 </script> 삽입 같은 문제를 막습니다."""
    return (
        json.dumps(data, ensure_ascii=False)
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
        .replace('&', '\\u0026')
    )


def _save_daily_planner(request):
    """'일과 전송' 버튼(POST, JSON)으로 오늘의 플래너를 DB에 저장합니다."""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        if not isinstance(payload, dict):
            raise ValueError('payload')

        todays_point = str(payload.get('todays_point', '')).strip()[:255]
        timetable_data = payload.get('timetable_data', {})
        todo_data = payload.get('todo_data', [])
        timer_data = payload.get('timer_data', {})

        if not isinstance(timetable_data, dict) or not isinstance(todo_data, list) or not isinstance(timer_data, dict):
            raise ValueError('shape')

        total_seconds = sum(
            max(0, int(v)) for v in timer_data.values()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        )

        planner, _created = DailyPlanner.objects.update_or_create(
            user=request.user,
            date=timezone.localdate(),
            defaults={
                'todays_point': todays_point,
                'timetable_data': timetable_data,
                'todo_data': todo_data,
                'timer_data': timer_data,
                'total_study_seconds': total_seconds,
            },
        )
    except (ValueError, TypeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': '전송한 데이터 형식이 올바르지 않습니다.'}, status=400)

    return JsonResponse({
        'status': 'success',
        'message': '오늘의 학습 플래너가 서버에 안전하게 저장되었습니다.',
        'updated_at': timezone.localtime(planner.updated_at).strftime('%H:%M:%S'),
    })


@planner_permission_required
def dashboard_view(request):
    """플래너 메인 대시보드 (기존 홈페이지 메뉴와 완전히 분리된 독립 화면)"""
    # '일과 전송' 버튼: 같은 주소(/planner/)로 POST 가 오면 저장 처리
    if request.method == 'POST':
        return _save_daily_planner(request)

    today = timezone.localdate()
    planner = DailyPlanner.objects.filter(user=request.user, date=today).first()

    profile = getattr(request.user, 'profile', None)
    user_display_name = profile.name if profile else (request.user.first_name or request.user.username)

    context = {
        'user_display_name': user_display_name,
        'profile': profile,
        'today': today,
        # 오늘 이미 저장한 내용이 있으면 화면에 복원
        'todays_point': planner.todays_point if planner else '',
        'saved_timetable_json': _json_for_script(planner.timetable_data if planner else {}),
        'saved_todo_json': _json_for_script(planner.todo_data if planner else []),
        'saved_timer_json': _json_for_script(planner.timer_data if planner else {}),
    }
    return render(request, 'planner/dashboard.html', context)
