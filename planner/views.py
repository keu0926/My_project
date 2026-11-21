import json
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

import calendar
from datetime import timedelta

from .models import DailyPlanner

# planner/views.py 상단 임포트에 추가
from total_schedule.models import ScheduleSeason, ClassSlot, StudentEnrollment, ClassLessonLog

from datetime import datetime, time, timedelta

# 할 일 목록에 허용하는 과목 -> 뱃지 클래스 (정해진 5과목 외에는 저장하지 않음)
TODO_SUBJECT_BADGES = {
    '국어': 'badge-kor',
    '수학': 'badge-math',
    '영어': 'badge-eng',
    '과탐': 'badge-sci',
    '사탐': 'badge-soc',
}
TODO_MAX_ITEMS = 200
TODO_MAX_TEXT_LENGTH = 300


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


def _clean_todo_items(items):
    """화면에서 받은 할 일 목록을 검증해서 정해진 형태로만 저장합니다.
    - 과목은 국어/수학/영어/과탐/사탐만 허용하고, 뱃지 클래스는 서버가 직접 정합니다.
    - 글은 그대로(태그 변환 없이) 저장하며, 화면에 그릴 때 이스케이프합니다."""
    cleaned = []
    for item in items[:TODO_MAX_ITEMS]:
        if not isinstance(item, dict):
            continue

        subject = item.get('subject')
        if subject not in TODO_SUBJECT_BADGES:
            continue

        text = str(item.get('text', '')).strip()[:TODO_MAX_TEXT_LENGTH]
        if not text:
            continue

        is_done = item.get('status') == 'complete'
        try:
            rate = int(item.get('rate', 0))
        except (TypeError, ValueError):
            rate = 0
        rate = max(0, min(100, rate))

        cleaned.append({
            'id': len(cleaned) + 1,
            'subject': subject,
            'badgeClass': TODO_SUBJECT_BADGES[subject],
            'text': text,
            'status': 'complete' if is_done else 'incomplete',
            'rate': 100 if is_done else rate,
        })
    return cleaned


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

        todo_data = _clean_todo_items(todo_data)

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
        'message': '오늘의 학습 기록이 저장되었습니다.',
        'updated_at': timezone.localtime(planner.updated_at).strftime('%H:%M:%S'),
    })


@planner_permission_required
def dashboard_view(request):
    """플래너 메인 대시보드 (기존 홈페이지 메뉴와 완전히 분리된 독립 화면)"""
    # '일과 전송' 버튼: 같은 주소(/planner/)로 POST 가 오면 저장 처리
    if request.method == 'POST':
        return _save_daily_planner(request)

    # 기존: today = timezone.localdate()
    # 수정: ?date=2026-11-23 형태로 접속하면 해당 날짜로 테스트 가능 (없으면 오늘 날짜)
    date_param = request.GET.get('date')
    if date_param:
        try:
            today = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            today = timezone.localdate()
    else:
        today = timezone.localdate()
        
    planner = DailyPlanner.objects.filter(user=request.user, date=today).first()

    profile = getattr(request.user, 'profile', None)
    user_display_name = profile.name if profile else (request.user.first_name or request.user.username)

    # ★ 오늘 요일 기준 학생 개인 수업 시간표 및 지난주 수업일지/과제 조회
    today_weekday = today.weekday()  # 0:월 ~ 6:일
    active_season = ScheduleSeason.objects.filter(is_active=True).first()
    today_classes = []

    if active_season and request.user.is_authenticated:
        enrollments = StudentEnrollment.objects.filter(student=request.user, season=active_season)
        for enr in enrollments:
            matched_slots = ClassSlot.objects.filter(
                season=active_season,
                day_of_week=today_weekday,
                subject=enr.subject,
                teacher_name=enr.teacher_name,
                class_name=enr.class_name,
            ).select_related('period').order_by('period__order')

            if not matched_slots:
                continue

            # 가장 최근(지난주) 수업 일지 및 과제 조회
            last_log = ClassLessonLog.objects.filter(
                season=active_season,
                subject=enr.subject,
                teacher_name=enr.teacher_name,
                class_name=enr.class_name,
                lesson_date__lt=today,
            ).order_by('-lesson_date').first()

            for sl in matched_slots:
                today_classes.append({
                    'period_name': sl.period.name,
                    'start_time': sl.period.start_time.strftime('%H:%M'),
                    'end_time': sl.period.end_time.strftime('%H:%M'),
                    'subject': sl.subject,
                    'teacher_name': sl.teacher_name,
                    'class_name': sl.class_name,
                    'last_lesson_date': last_log.lesson_date.strftime('%Y-%m-%d') if last_log else '',
                    'last_content': last_log.content if last_log else '',
                    'last_homework': last_log.homework if last_log else '',
                })

    today_classes.sort(key=lambda x: x['start_time'])


    context = {
        'user_display_name': user_display_name,
        'profile': profile,
        'today': today,
        # 오늘 이미 저장한 내용이 있으면 화면에 복원
        'todays_point': planner.todays_point if planner else '',
        'saved_timetable_json': _json_for_script(planner.timetable_data if planner else {}),
        'saved_todo_json': _json_for_script(planner.todo_data if planner else []),
        'saved_timer_json': _json_for_script(planner.timer_data if planner else {}),
        'today_classes_json': json.dumps(today_classes, ensure_ascii=False),
        'today_classes': today_classes,
    }
    return render(request, 'planner/dashboard.html', context)

@planner_permission_required
def stats_view(request):
    """일별 · 주별 · 월별 학습 통계 시각화 페이지"""
    today = timezone.localdate()
    subjects = ['국어', '수학', '영어', '과탐', '사탐']

    # 1. [일별] 오늘 데이터 (계획 시간 vs 실제 순공 시간, 투두 달성률)
    today_planner = DailyPlanner.objects.filter(user=request.user, date=today).first()
    daily_actual_sec = {s: 0 for s in subjects}
    daily_plan_min = {s: 0 for s in subjects}
    todo_avg_rate = 0
    todo_total_count = 0
    todo_done_count = 0

    if today_planner:
        for s in subjects:
            daily_actual_sec[s] = int(today_planner.timer_data.get(s, 0) or 0)

        # 타임테이블 1칸 = 10분 기준으로 과목별 계획 시간 계산
        for slot_info in today_planner.timetable_data.values():
            if isinstance(slot_info, dict):
                subj = slot_info.get('subject')
                if subj in daily_plan_min:
                    daily_plan_min[subj] += 10

        todos = today_planner.todo_data or []
        todo_total_count = len(todos)
        if todo_total_count > 0:
            todo_done_count = sum(1 for t in todos if t.get('status') == 'complete')
            todo_avg_rate = round(sum(int(t.get('rate', 0)) for t in todos) / todo_total_count)

    # 2. [주별] 최근 7일 (6일 전 ~ 오늘) 요일별·과목별 누적 순공 시간
    week_start = today - timedelta(days=6)
    week_planners = {
        p.date: p for p in DailyPlanner.objects.filter(user=request.user, date__range=[week_start, today])
    }
    weekday_names = ['월', '화', '수', '목', '금', '토', '일']
    weekly_labels = []
    weekly_by_subject = {s: [] for s in subjects}
    weekly_total_seconds = 0

    for i in range(7):
        d = week_start + timedelta(days=i)
        weekly_labels.append(f"{d.month}/{d.day}({weekday_names[d.weekday()]})")
        p = week_planners.get(d)
        for s in subjects:
            sec = int(p.timer_data.get(s, 0) or 0) if p else 0
            weekly_by_subject[s].append(round(sec / 3600, 2)) # 시간(h) 단위 변환
            weekly_total_seconds += sec

    # 3. [월별] 이번 달 일별 학습 잔디 히트맵 & 주차별 과목 추이
    _, last_day = calendar.monthrange(today.year, today.month)
    month_start = today.replace(day=1)
    month_end = today.replace(day=last_day)
    month_planners = {
        p.date: p for p in DailyPlanner.objects.filter(user=request.user, date__range=[month_start, month_end])
    }

    # 달력 시작 요일 맞추기 (일요일 시작 기준 빈칸 개수)
    first_weekday = (month_start.weekday() + 1) % 7
    calendar_cells = [{'empty': True} for _ in range(first_weekday)]

    monthly_total_seconds = 0
    active_days = 0
    weekly_trend = {s: [0, 0, 0, 0, 0] for s in subjects} # 최대 5주

    for day_num in range(1, last_day + 1):
        d = today.replace(day=day_num)
        p = month_planners.get(d)
        sec = p.total_study_seconds if p else 0
        monthly_total_seconds += sec
        if sec > 0:
            active_days += 1

        # 잔디 농도 레벨 (0~4)
        hours = sec / 3600
        if sec == 0:
            level = 0
        elif hours < 2:
            level = 1
        elif hours < 4:
            level = 2
        elif hours < 7:
            level = 3
        else:
            level = 4

        calendar_cells.append({
            'empty': False,
            'day': day_num,
            'hours': round(hours, 1),
            'level': level,
            'is_today': d == today,
        })

        week_idx = min((day_num - 1) // 7, 4)
        if p:
            for s in subjects:
                s_sec = int(p.timer_data.get(s, 0) or 0)
                weekly_trend[s][week_idx] = round(weekly_trend[s][week_idx] + (s_sec / 3600), 2)

    profile = getattr(request.user, 'profile', None)
    user_display_name = profile.name if profile else (request.user.first_name or request.user.username)

    stats_payload = {
        'subjects': subjects,
        'daily': {
            'actual_min': [round(daily_actual_sec[s] / 60, 1) for s in subjects],
            'plan_min': [daily_plan_min[s] for s in subjects],
            'todo_avg_rate': todo_avg_rate,
            'todo_done_count': todo_done_count,
            'todo_total_count': todo_total_count,
        },
        'weekly': {
            'labels': weekly_labels,
            'by_subject': weekly_by_subject,
        },
        'monthly': {
            'year': today.year,
            'month': today.month,
            'calendar_cells': calendar_cells,
            'weekly_trend': weekly_trend,
        }
    }

    context = {
        'user_display_name': user_display_name,
        'today': today,
        'today_total_hours': round(sum(daily_actual_sec.values()) / 3600, 1),
        'weekly_avg_hours': round((weekly_total_seconds / 7) / 3600, 1),
        'monthly_total_hours': round(monthly_total_seconds / 3600, 1),
        'active_days': active_days,
        'todo_avg_rate': todo_avg_rate,
        'stats_json': _json_for_script(stats_payload),
    }
    return render(request, 'planner/stats.html', context)
