import json
from datetime import time
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db import models
from django.http import JsonResponse
from django.shortcuts import redirect, render

from total_schedule.models import ScheduleSeason, PeriodConfig, ClassSlot, StudentEnrollment

User = get_user_model()

DEFAULT_PERIODS = [
    ('1교시', False, 1, time(9, 0), time(10, 0)),
    ('2교시', False, 2, time(10, 0), time(11, 0)),
    ('3교시', False, 3, time(11, 0), time(12, 0)),
    ('4교시', False, 4, time(12, 0), time(13, 0)),
    ('점심 시간', True, 5, time(13, 0), time(14, 0)),
    ('5교시', False, 6, time(14, 0), time(15, 0)),
    ('6교시', False, 7, time(15, 0), time(16, 0)),
    ('7교시', False, 8, time(16, 0), time(17, 0)),
    ('8교시', False, 9, time(17, 0), time(18, 0)),
    ('저녁 시간', True, 10, time(18, 0), time(19, 0)),
    ('9교시', False, 11, time(19, 0), time(20, 0)),
    ('10교시', False, 12, time(20, 0), time(21, 0)),
    ('11교시', False, 13, time(21, 0), time(22, 0)),
    ('12교시', False, 14, time(22, 0), time(23, 0)),
]


def _ensure_season_periods(season):
    if not season.periods.exists():
        PeriodConfig.objects.bulk_create([
            PeriodConfig(season=season, name=name, is_break=is_brk, order=order, start_time=st, end_time=et)
            for name, is_brk, order, st, et in DEFAULT_PERIODS
        ])


@staff_member_required(login_url='/login/')
def dashboard_redirect_view(request):
    return redirect('academy_admin:schedule_manage')


@staff_member_required(login_url='/login/')
def manage_schedule_view(request):
    """관리자 전용: 시즌별 학원 토탈스케줄 편성 및 교시 시간 유동 설정"""
    seasons = ScheduleSeason.objects.all()
    if not seasons.exists():
        default_season = ScheduleSeason.objects.create(name='기본 시즌 스케줄', is_active=True)
        _ensure_season_periods(default_season)
        seasons = ScheduleSeason.objects.all()

    season_id = request.GET.get('season') or request.POST.get('season_id')
    if season_id:
        current_season = ScheduleSeason.objects.filter(id=season_id).first() or seasons.first()
    else:
        current_season = seasons.filter(is_active=True).first() or seasons.first()

    _ensure_season_periods(current_season)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
            action = payload.get('action')

            if action == 'create_season':
                name = str(payload.get('name', '')).strip()[:100]
                if not name:
                    return JsonResponse({'status': 'error', 'message': '시즌 이름을 입력해 주세요.'}, status=400)
                copy_from_id = payload.get('copy_from_id')
                new_season = ScheduleSeason.objects.create(name=name, is_active=bool(payload.get('set_active', True)))
                if new_season.is_active:
                    ScheduleSeason.objects.exclude(id=new_season.id).update(is_active=False)

                if copy_from_id:
                    src = ScheduleSeason.objects.filter(id=copy_from_id).first()
                    if src:
                        period_map = {}
                        for p in src.periods.all():
                            new_p = PeriodConfig.objects.create(
                                season=new_season, name=p.name, is_break=p.is_break, order=p.order,
                                start_time=p.start_time, end_time=p.end_time
                            )
                            period_map[p.id] = new_p
                        ClassSlot.objects.bulk_create([
                            ClassSlot(
                                season=new_season, day_of_week=s.day_of_week, period=period_map[s.period_id],
                                subject=s.subject, teacher_user=s.teacher_user, teacher_name=s.teacher_name,
                                class_name=s.class_name, is_merged=s.is_merged
                            )
                            for s in src.class_slots.all() if s.period_id in period_map
                        ])
                _ensure_season_periods(new_season)
                return JsonResponse({'status': 'success', 'season_id': new_season.id})

            if action == 'activate_season':
                ScheduleSeason.objects.all().update(is_active=False)
                current_season.is_active = True
                current_season.save(update_fields=['is_active'])
                return JsonResponse({'status': 'success', 'message': f'[{current_season.name}] 시즌이 현재 적용 시즌으로 설정되었습니다.'})

            if action == 'save_periods':
                for item in payload.get('periods', []):
                    p_obj = PeriodConfig.objects.filter(id=item.get('id'), season=current_season).first()
                    if p_obj:
                        sh, sm = map(int, item['start_time'].split(':'))
                        eh, em = map(int, item['end_time'].split(':'))
                        p_obj.start_time = time(sh, sm)
                        p_obj.end_time = time(eh, em)
                        p_obj.save(update_fields=['start_time', 'end_time'])
                return JsonResponse({'status': 'success', 'message': '교시별 시간 설정이 저장되었습니다.'})

            if action == 'update_single_period':
                p_obj = PeriodConfig.objects.filter(id=payload.get('period_id'), season=current_season).first()
                if not p_obj:
                    return JsonResponse({'status': 'error', 'message': '교시를 찾을 수 없습니다.'}, status=404)

                old_end_min = p_obj.end_time.hour * 60 + p_obj.end_time.minute
                sh, sm = map(int, payload['start_time'].split(':'))
                eh, em = map(int, payload['end_time'].split(':'))
                new_end_min = eh * 60 + em

                if new_end_min <= (sh * 60 + sm):
                    return JsonResponse({'status': 'error', 'message': '종료 시각은 시작 시각보다 늦어야 합니다.'}, status=400)

                p_obj.name = str(payload.get('name', p_obj.name)).strip()[:50] or p_obj.name
                p_obj.start_time = time(sh, sm)
                p_obj.end_time = time(eh, em)
                p_obj.save(update_fields=['name', 'start_time', 'end_time'])

                diff_min = new_end_min - old_end_min
                if payload.get('cascade') and diff_min != 0:
                    following = PeriodConfig.objects.filter(season=current_season, order__gt=p_obj.order)
                    for fp in following:
                        s_tot = max(0, min(23 * 60 + 59, fp.start_time.hour * 60 + fp.start_time.minute + diff_min))
                        e_tot = max(0, min(23 * 60 + 59, fp.end_time.hour * 60 + fp.end_time.minute + diff_min))
                        fp.start_time = time(s_tot // 60, s_tot % 60)
                        fp.end_time = time(e_tot // 60, e_tot % 60)
                        fp.save(update_fields=['start_time', 'end_time'])

                return JsonResponse({'status': 'success'})

            if action == 'add_period':
                name = str(payload.get('name', '')).strip()[:50] or '추가 교시'
                sh, sm = map(int, payload['start_time'].split(':'))
                eh, em = map(int, payload['end_time'].split(':'))
                last_order = current_season.periods.aggregate(models.Max('order'))['order__max'] or 0
                PeriodConfig.objects.create(
                    season=current_season,
                    name=name,
                    is_break=bool(payload.get('is_break', False)),
                    order=last_order + 1,
                    start_time=time(sh, sm),
                    end_time=time(eh, em),
                )
                return JsonResponse({'status': 'success'})

            if action == 'delete_period':
                PeriodConfig.objects.filter(id=payload.get('period_id'), season=current_season).delete()
                return JsonResponse({'status': 'success'})

            if action == 'add_slots':
                targets = payload.get('targets', [])
                subject = payload.get('subject', '국어')
                teacher_name = str(payload.get('teacher_name', '')).strip()[:50]
                class_name = str(payload.get('class_name', '')).strip()[:100]
                confirm_merged = bool(payload.get('confirm_merged', False))

                if not targets or not class_name:
                    return JsonResponse({'status': 'error', 'message': '교시를 선택하고 반명(또는 활동명)을 입력해 주세요.'}, status=400)

                conflict_details = []
                for t in targets:
                    day = int(t['day'])
                    pid = int(t['period_id'])
                    existing_qs = ClassSlot.objects.filter(season=current_season, day_of_week=day, period_id=pid)

                    if existing_qs.count() >= 10:
                        return JsonResponse({
                            'status': 'error',
                            'message': '동일한 요일과 시간대에는 최대 10명 강사까지만 배치할 수 있습니다.'
                        }, status=400)

                    if teacher_name:
                        same_teacher = existing_qs.filter(teacher_name=teacher_name).first()
                        if same_teacher:
                            p_label = same_teacher.period.name
                            day_label = dict(ClassSlot.DAY_CHOICES).get(day, '')
                            conflict_details.append(f"{day_label} {p_label} ({same_teacher.subject} {same_teacher.class_name})")

                if conflict_details and not confirm_merged:
                    return JsonResponse({
                        'status': 'confirm_merge',
                        'message': f"같은 시간대에 [{teacher_name}] 선생님이 이미 배치되어 있습니다.\n({', '.join(conflict_details)})\n\n합반입니까?"
                    })

                created_count = 0
                for t in targets:
                    day = int(t['day'])
                    pid = int(t['period_id'])
                    period_obj = PeriodConfig.objects.filter(id=pid, season=current_season).first()
                    if not period_obj:
                        continue

                    is_merged_flag = False
                    if teacher_name:
                        existing_same = ClassSlot.objects.filter(
                            season=current_season, day_of_week=day, period=period_obj, teacher_name=teacher_name
                        )
                        if existing_same.exists():
                            is_merged_flag = True
                            existing_same.update(is_merged=True)

                    ClassSlot.objects.create(
                        season=current_season,
                        day_of_week=day,
                        period=period_obj,
                        subject=subject,
                        teacher_name=teacher_name,
                        class_name=class_name,
                        is_merged=is_merged_flag,
                    )
                    created_count += 1

                return JsonResponse({'status': 'success', 'message': f'{created_count}개 시간대에 수업이 등록되었습니다.'})

            if action == 'delete_slot':
                ClassSlot.objects.filter(id=payload.get('slot_id'), season=current_season).delete()
                return JsonResponse({'status': 'success', 'message': '삭제되었습니다.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'처리 중 오류: {str(e)}'}, status=400)

    periods = list(current_season.periods.all())
    slots = list(current_season.class_slots.select_related('period').all())

    days = [
        {'idx': 0, 'name': '월요일'}, {'idx': 1, 'name': '화요일'}, {'idx': 2, 'name': '수요일'},
        {'idx': 3, 'name': '목요일'}, {'idx': 4, 'name': '금요일'}, {'idx': 5, 'name': '토요일'},
        {'idx': 6, 'name': '일요일'},
    ]

    slot_lookup = {}
    for s in slots:
        slot_lookup.setdefault((s.period_id, s.day_of_week), []).append({
            'id': s.id,
            'subject': s.subject,
            'teacher_name': s.teacher_name,
            'class_name': s.class_name,
            'is_merged': s.is_merged,
        })

    grid_rows = []
    for p in periods:
        row_cells = []
        for d in days:
            row_cells.append({
                'day_idx': d['idx'],
                'slots': slot_lookup.get((p.id, d['idx']), []),
            })
        grid_rows.append({
            'period': p,
            'is_break': p.is_break,
            'cells': row_cells,
        })

    context = {
        'seasons': seasons,
        'current_season': current_season,
        'periods': periods,
        'days': days,
        'grid_rows': grid_rows,
    }
    return render(request, 'academy_admin/schedule_manage.html', context)


@staff_member_required(login_url='/login/')
def student_enroll_view(request):
    """관리자 전용: 회원 가입한 학생별 수강 반 배정 및 동시간대 충돌 검증"""
    seasons = ScheduleSeason.objects.all()
    season_id = request.GET.get('season') or request.POST.get('season_id')
    if season_id:
        current_season = ScheduleSeason.objects.filter(id=season_id).first() or seasons.first()
    else:
        current_season = seasons.filter(is_active=True).first() or seasons.first()

    if not current_season:
        return render(request, 'academy_admin/student_enroll.html', {'no_season': True})

    students = list(User.objects.filter(is_staff=False, is_superuser=False).order_by('first_name', 'username'))
    selected_student_id = request.GET.get('student') or request.POST.get('student_id')
    current_student = None
    if students:
        if selected_student_id:
            current_student = next((u for u in students if str(u.id) == str(selected_student_id)), students[0])
        else:
            current_student = students[0]

    all_slots = list(current_season.class_slots.select_related('period').order_by('day_of_week', 'period__order'))
    day_names = ['월', '화', '수', '목', '금', '토', '일']

    course_map = {}
    for s in all_slots:
        key = (s.subject, s.teacher_name, s.class_name)
        if key not in course_map:
            course_map[key] = {
                'subject': s.subject,
                'teacher_name': s.teacher_name,
                'class_name': s.class_name,
                'slots': [],
                'schedule_texts': [],
            }
        course_map[key]['slots'].append((s.day_of_week, s.period_id))
        course_map[key]['schedule_texts'].append(
            f"{day_names[s.day_of_week]} {s.period.name}({s.period.start_time:%H:%M}~{s.period.end_time:%H:%M})"
        )

    available_courses = sorted(course_map.values(), key=lambda x: (x['subject'], x['teacher_name'], x['class_name']))

    if request.method == 'POST' and current_student:
        try:
            payload = json.loads(request.body.decode('utf-8'))
            action = payload.get('action')

            if action == 'enroll':
                subject = payload.get('subject', '')
                teacher_name = payload.get('teacher_name', '')
                class_name = payload.get('class_name', '')

                target_course = course_map.get((subject, teacher_name, class_name))
                if not target_course:
                    return JsonResponse({'status': 'error', 'message': '토탈스케줄에 존재하지 않는 강좌입니다.'}, status=400)

                if StudentEnrollment.objects.filter(
                    student=current_student, season=current_season,
                    subject=subject, teacher_name=teacher_name, class_name=class_name
                ).exists():
                    return JsonResponse({'status': 'error', 'message': '이미 해당 학생에게 배정된 반입니다.'}, status=400)

                existing_enrollments = StudentEnrollment.objects.filter(student=current_student, season=current_season)
                occupied = {}
                for enr in existing_enrollments:
                    enr_course = course_map.get((enr.subject, enr.teacher_name, enr.class_name))
                    if enr_course:
                        for dp in enr_course['slots']:
                            occupied[dp] = f"{enr.subject}({enr.teacher_name} {enr.class_name})".strip()

                conflicts = []
                period_lookup = {p.id: p for p in current_season.periods.all()}
                for day_idx, pid in target_course['slots']:
                    if (day_idx, pid) in occupied:
                        p_obj = period_lookup.get(pid)
                        p_name = p_obj.name if p_obj else ''
                        conflicts.append(f"{day_names[day_idx]}요일 {p_name} — 기존 [{occupied[(day_idx, pid)]}] 수업과 겹침")

                if conflicts:
                    return JsonResponse({
                        'status': 'conflict',
                        'message': "⚠️ 시간표 충돌로 배정할 수 없습니다!\n\n" + "\n".join(conflicts)
                    }, status=400)

                StudentEnrollment.objects.create(
                    student=current_student,
                    season=current_season,
                    subject=subject,
                    teacher_name=teacher_name,
                    class_name=class_name,
                )
                return JsonResponse({'status': 'success'})

            if action == 'unenroll':
                StudentEnrollment.objects.filter(id=payload.get('enrollment_id'), student=current_student).delete()
                return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    student_enrollments = []
    student_slot_lookup = {}
    if current_student:
        student_enrollments = list(
            StudentEnrollment.objects.filter(student=current_student, season=current_season).order_by('subject', 'id')
        )
        for enr in student_enrollments:
            matched_slots = [
                s for s in all_slots
                if s.subject == enr.subject and s.teacher_name == enr.teacher_name and s.class_name == enr.class_name
            ]
            for s in matched_slots:
                student_slot_lookup[(s.period_id, s.day_of_week)] = {
                    'subject': s.subject,
                    'teacher_name': s.teacher_name,
                    'class_name': s.class_name,
                }

    periods = list(current_season.periods.all())
    days = [
        {'idx': 0, 'name': '월'}, {'idx': 1, 'name': '화'}, {'idx': 2, 'name': '수'},
        {'idx': 3, 'name': '목'}, {'idx': 4, 'name': '금'}, {'idx': 5, 'name': '토'}, {'idx': 6, 'name': '일'},
    ]
    preview_rows = []
    for p in periods:
        preview_rows.append({
            'period': p,
            'cells': [student_slot_lookup.get((p.id, d['idx'])) for d in days]
        })

    context = {
        'seasons': seasons,
        'current_season': current_season,
        'students': students,
        'current_student': current_student,
        'available_courses': available_courses,
        'student_enrollments': student_enrollments,
        'days': days,
        'preview_rows': preview_rows,
    }
    return render(request, 'academy_admin/student_enroll.html', context)