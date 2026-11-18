import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from planner.models import DailyPlanner


@csrf_exempt
def dashboard(request):
    # '하루 일과 전송' 버튼을 누를 때 (POST 요청)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': '로그인이 필요합니다.'}, status=401)
        try:
            payload = json.loads(request.body.decode('utf-8'))
            today = timezone.localdate()

            todays_point = payload.get('todays_point', '').strip()
            timetable_data = payload.get('timetable_data', {})
            todo_data = payload.get('todo_data', [])
            timer_data = payload.get('timer_data', {})

            total_seconds = sum(int(v) for v in timer_data.values() if isinstance(v, (int, float)))

            planner, created = DailyPlanner.objects.update_or_create(
                user=request.user,
                date=today,
                defaults={
                    'todays_point': todays_point,
                    'timetable_data': timetable_data,
                    'todo_data': todo_data,
                    'timer_data': timer_data,
                    'total_study_seconds': total_seconds,
                }
            )

            return JsonResponse({
                'status': 'success',
                'message': '오늘의 학습 플래너가 서버에 안전하게 저장되었습니다.',
                'updated_at': timezone.localtime(planner.updated_at).strftime('%H:%M:%S')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # 평소 페이지에 접속할 때 (GET 요청)
    if not request.user.is_authenticated:
        return redirect('login')

    today = timezone.localdate()
    planner = DailyPlanner.objects.filter(user=request.user, date=today).first()
    user_display_name = getattr(request.user, 'name', '') or request.user.first_name or request.user.username

    context = {
        'today': today,
        'user_display_name': user_display_name,
        'todays_point': planner.todays_point if planner else '',
        'saved_timetable_json': json.dumps(planner.timetable_data if planner else {}, ensure_ascii=False),
        'saved_todo_json': json.dumps(planner.todo_data if planner else [], ensure_ascii=False),
        'saved_timer_json': json.dumps(planner.timer_data if planner else {}, ensure_ascii=False),
    }
    return render(request, 'planner/dashboard.html', context)