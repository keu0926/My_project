import json
import logging
from datetime import time

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render

from total_schedule.models import ScheduleSeason, PeriodConfig, ClassSlot, StudentEnrollment

logger = logging.getLogger(__name__)
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

VALID_DAYS = {value for value, _label in ClassSlot.DAY_CHOICES}
VALID_SUBJECTS = {value for value, _label in ClassSlot.SUBJECT_CHOICES}
DAY_NAMES = ['월', '화', '수', '목', '금', '토', '일']

MAX_SLOT_TARGETS = 300          # 한 번에 배정할 수 있는 칸 수
MAX_TEACHERS_PER_CELL = 10      # 동일 요일·교시에 배치 가능한 최대 강사 수
LAST_MINUTE_OF_DAY = 23 * 60 + 59


class ActionError(Exception):
    """사용자에게 그대로 보여줄 수 있는 입력 오류.
    처리 중이던 DB 변경은 모두 취소(롤백)됩니다."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


# ---------------------------------------------------------------------------
# 공통 도구
# ---------------------------------------------------------------------------
def _run_action(handler, *args):
    """한 번의 요청에서 일어나는 모든 DB 변경을 하나의 트랜잭션으로 묶어 실행합니다.
    중간에 오류가 나면 일부만 저장되지 않고 전부 취소됩니다."""
    try:
        with transaction.atomic():
            return handler(*args)
    except ActionError as exc:
        return JsonResponse({'status': 'error', 'message': exc.message}, status=exc.status)
    except Exception:
        # 내부 오류 문구는 화면에 내보내지 않고 서버 로그에만 남깁니다.
        logger.exception('academy_admin 요청 처리 중 오류')
        return JsonResponse(
            {'status': 'error', 'message': '처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'},
            status=500,
        )


def _read_payload(request):
    if request.method == 'POST' and request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
            return data if isinstance(data, dict) else {}
        except (ValueError, UnicodeDecodeError):
            return {}
    return {}


def _pick_season(request, payload, seasons):
    season_id = request.GET.get('season') or request.POST.get('season_id') or payload.get('season_id')
    if season_id:
        try:
            found = seasons.filter(id=int(season_id)).first()
        except (TypeError, ValueError):
            found = None
        return found or seasons.first()
    return seasons.filter(is_active=True).first() or seasons.first()


def _to_int(value, label):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ActionError(f'{label} 값이 올바르지 않습니다.')


def _parse_hhmm(value):
    try:
        hour_str, minute_str = str(value).split(':')[:2]
        return time(int(hour_str), int(minute_str))
    except (ValueError, TypeError):
        raise ActionError('시각은 HH:MM 형식(00:00~23:59)으로 입력해 주세요.')


def _minutes(t):
    return t.hour * 60 + t.minute


def _parse_time_range(start_value, end_value):
    start = _parse_hhmm(start_value)
    end = _parse_hhmm(end_value)
    if _minutes(end) <= _minutes(start):
        raise ActionError('종료 시각은 시작 시각보다 늦어야 합니다.')
    return start, end


def _day_label(day_idx):
    return DAY_NAMES[day_idx] if 0 <= day_idx < len(DAY_NAMES) else '?'


def _ensure_season_periods(season):
    with transaction.atomic():
        if not season.periods.exists():
            PeriodConfig.objects.bulk_create([
                PeriodConfig(season=season, name=name, is_break=is_brk, order=order, start_time=st, end_time=et)
                for name, is_brk, order, st, et in DEFAULT_PERIODS
            ])


def _orphaned_enrollments(season, removing_slots):
    """삭제하려는 수업 칸(removing_slots)이 사라지면 시간표 어디에도 남지 않게 되는 반을
    수강 중인 학생 배정(StudentEnrollment) 목록을 돌려줍니다.
    (수강 배정은 과목·강사명·반명 문자열로 수업과 연결되어 있어서, 수업이 모두 사라지면 고아가 됩니다.)"""
    removed_ids = list(removing_slots.values_list('id', flat=True))
    if not removed_ids:
        return StudentEnrollment.objects.none()

    removed_keys = set(removing_slots.values_list('subject', 'teacher_name', 'class_name'))
    remaining_keys = set(
        ClassSlot.objects.filter(season=season)
        .exclude(id__in=removed_ids)
        .values_list('subject', 'teacher_name', 'class_name')
    )
    orphan_keys = removed_keys - remaining_keys
    if not orphan_keys:
        return StudentEnrollment.objects.none()

    condition = Q()
    for subject, teacher_name, class_name in orphan_keys:
        condition |= Q(subject=subject, teacher_name=teacher_name, class_name=class_name)
    return StudentEnrollment.objects.filter(season=season).filter(condition)


# ---------------------------------------------------------------------------
# 1. 토탈스케줄 편성
# ---------------------------------------------------------------------------
def _handle_schedule_action(payload, current_season):
    action = payload.get('action')

    if action == 'create_season':
        name = str(payload.get('name', '')).strip()[:100]
        if not name:
            raise ActionError('시즌 이름을 입력해 주세요.')

        set_active = bool(payload.get('set_active', True))
        new_season = ScheduleSeason.objects.create(name=name, is_active=set_active)
        if set_active:
            ScheduleSeason.objects.exclude(id=new_season.id).update(is_active=False)

        copy_from_id = payload.get('copy_from_id')
        if copy_from_id:
            src = ScheduleSeason.objects.filter(id=_to_int(copy_from_id, '복사할 시즌')).first()
            if src:
                period_map = {}
                for p in src.periods.all():
                    period_map[p.id] = PeriodConfig.objects.create(
                        season=new_season, name=p.name, is_break=p.is_break, order=p.order,
                        start_time=p.start_time, end_time=p.end_time,
                    )
                ClassSlot.objects.bulk_create([
                    ClassSlot(
                        season=new_season, day_of_week=s.day_of_week, period=period_map[s.period_id],
                        subject=s.subject, teacher_user=s.teacher_user, teacher_name=s.teacher_name,
                        class_name=s.class_name, is_merged=s.is_merged,
                    )
                    for s in src.class_slots.all() if s.period_id in period_map
                ])
        _ensure_season_periods(new_season)
        return JsonResponse({'status': 'success', 'season_id': new_season.id})

    if action == 'activate_season':
        ScheduleSeason.objects.all().update(is_active=False)
        current_season.is_active = True
        current_season.save(update_fields=['is_active'])
        return JsonResponse({
            'status': 'success',
            'message': f'[{current_season.name}] 시즌이 현재 적용 시즌으로 설정되었습니다.',
        })

    if action == 'save_periods':
        items = payload.get('periods', [])
        if not isinstance(items, list):
            raise ActionError('교시 목록 형식이 올바르지 않습니다.')

        for item in items:
            if not isinstance(item, dict):
                continue
            p_obj = PeriodConfig.objects.filter(
                id=_to_int(item.get('id'), '교시'), season=current_season
            ).first()
            if not p_obj:
                continue
            try:
                start, end = _parse_time_range(item.get('start_time'), item.get('end_time'))
            except ActionError as exc:
                raise ActionError(f'[{p_obj.name}] {exc.message}')
            p_obj.start_time = start
            p_obj.end_time = end
            p_obj.save(update_fields=['start_time', 'end_time'])
        return JsonResponse({'status': 'success', 'message': '교시별 시간 설정이 저장되었습니다.'})

    if action == 'update_single_period':
        p_obj = PeriodConfig.objects.filter(
            id=_to_int(payload.get('period_id'), '교시'), season=current_season
        ).first()
        if not p_obj:
            raise ActionError('교시를 찾을 수 없습니다.', status=404)

        start, end = _parse_time_range(payload.get('start_time'), payload.get('end_time'))
        old_end_min = _minutes(p_obj.end_time)

        p_obj.name = str(payload.get('name', p_obj.name)).strip()[:50] or p_obj.name
        p_obj.start_time = start
        p_obj.end_time = end
        p_obj.save(update_fields=['name', 'start_time', 'end_time'])

        diff_min = _minutes(end) - old_end_min
        if payload.get('cascade') and diff_min != 0:
            following = list(PeriodConfig.objects.filter(season=current_season, order__gt=p_obj.order))
            shifted = []
            for fp in following:
                s_tot = _minutes(fp.start_time) + diff_min
                e_tot = _minutes(fp.end_time) + diff_min
                if s_tot < 0 or e_tot > LAST_MINUTE_OF_DAY:
                    raise ActionError(
                        '뒤 교시를 함께 밀면 하루(00:00~23:59) 범위를 벗어납니다. '
                        '자동으로 밀기를 끄거나 시간을 줄여 주세요.'
                    )
                shifted.append((fp, s_tot, e_tot))
            for fp, s_tot, e_tot in shifted:
                fp.start_time = time(s_tot // 60, s_tot % 60)
                fp.end_time = time(e_tot // 60, e_tot % 60)
                fp.save(update_fields=['start_time', 'end_time'])

        return JsonResponse({'status': 'success'})

    if action == 'add_period':
        name = str(payload.get('name', '')).strip()[:50] or '추가 교시'
        start, end = _parse_time_range(payload.get('start_time'), payload.get('end_time'))
        last_order = current_season.periods.aggregate(Max('order'))['order__max'] or 0
        PeriodConfig.objects.create(
            season=current_season,
            name=name,
            is_break=bool(payload.get('is_break', False)),
            order=last_order + 1,
            start_time=start,
            end_time=end,
        )
        return JsonResponse({'status': 'success'})

    if action == 'delete_period':
        p_obj = PeriodConfig.objects.filter(
            id=_to_int(payload.get('period_id'), '교시'), season=current_season
        ).first()
        if not p_obj:
            raise ActionError('교시를 찾을 수 없습니다.', status=404)

        slots = ClassSlot.objects.filter(season=current_season, period=p_obj)
        orphan_ids = list(_orphaned_enrollments(current_season, slots).values_list('id', flat=True))
        if orphan_ids and not payload.get('confirm_unenroll'):
            return JsonResponse({
                'status': 'confirm_unenroll',
                'message': (
                    f'이 교시를 삭제하면 이 교시에만 남아 있던 반을 수강 중인 학생 배정 {len(orphan_ids)}건도 '
                    '함께 해제됩니다.\n계속하시겠습니까?'
                ),
            })

        if orphan_ids:
            StudentEnrollment.objects.filter(id__in=orphan_ids).delete()
        p_obj.delete()  # 이 교시의 수업 칸은 함께 삭제됩니다.
        return JsonResponse({'status': 'success'})

    if action == 'add_slots':
        subject = str(payload.get('subject', '')).strip()
        teacher_name = str(payload.get('teacher_name', '')).strip()[:50]
        class_name = str(payload.get('class_name', '')).strip()[:100]
        confirm_merged = bool(payload.get('confirm_merged', False))
        targets_raw = payload.get('targets', [])

        if not isinstance(targets_raw, list) or not targets_raw or not class_name:
            raise ActionError('교시를 선택하고 반명(또는 활동명)을 입력해 주세요.')
        if subject not in VALID_SUBJECTS:
            raise ActionError('과목이 올바르지 않습니다.')
        if len(targets_raw) > MAX_SLOT_TARGETS:
            raise ActionError(f'한 번에 배정할 수 있는 칸은 최대 {MAX_SLOT_TARGETS}개입니다.')

        targets = []
        seen = set()
        for t in targets_raw:
            if not isinstance(t, dict):
                raise ActionError('선택한 칸 정보가 올바르지 않습니다.')
            day = _to_int(t.get('day'), '요일')
            pid = _to_int(t.get('period_id'), '교시')
            if day not in VALID_DAYS:
                raise ActionError('요일이 올바르지 않습니다.')
            if (day, pid) in seen:
                continue
            seen.add((day, pid))
            targets.append((day, pid))

        period_ids = {pid for _day, pid in targets}
        periods = {p.id: p for p in PeriodConfig.objects.filter(season=current_season, id__in=period_ids)}
        if len(periods) != len(period_ids):
            raise ActionError('현재 시즌에 없는 교시가 포함되어 있습니다. 새로고침 후 다시 시도해 주세요.')

        conflict_details = []
        for day, pid in targets:
            existing_qs = ClassSlot.objects.filter(season=current_season, day_of_week=day, period_id=pid)
            if existing_qs.count() >= MAX_TEACHERS_PER_CELL:
                raise ActionError('동일한 요일과 시간대에는 최대 10명 강사까지만 배치할 수 있습니다.')

            if teacher_name:
                same_teacher = existing_qs.filter(teacher_name=teacher_name).first()
                if same_teacher:
                    day_label = dict(ClassSlot.DAY_CHOICES).get(day, '')
                    conflict_details.append(
                        f"{day_label} {periods[pid].name} ({same_teacher.subject} {same_teacher.class_name})"
                    )

        if conflict_details and not confirm_merged:
            return JsonResponse({
                'status': 'confirm_merge',
                'message': (
                    f"같은 시간대에 [{teacher_name}] 선생님이 이미 배치되어 있습니다.\n"
                    f"({', '.join(conflict_details)})\n\n합반입니까?"
                ),
            })

        created_count = 0
        for day, pid in targets:
            period_obj = periods[pid]

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
        slot_qs = ClassSlot.objects.filter(id=_to_int(payload.get('slot_id'), '수업'), season=current_season)
        if not slot_qs.exists():
            raise ActionError('수업을 찾을 수 없습니다. 새로고침 후 다시 시도해 주세요.', status=404)

        orphan_ids = list(_orphaned_enrollments(current_season, slot_qs).values_list('id', flat=True))
        if orphan_ids and not payload.get('confirm_unenroll'):
            return JsonResponse({
                'status': 'confirm_unenroll',
                'message': (
                    f'이 수업을 삭제하면 이 반을 수강 중인 학생 배정 {len(orphan_ids)}건도 함께 해제됩니다.\n'
                    '계속하시겠습니까?'
                ),
            })

        if orphan_ids:
            StudentEnrollment.objects.filter(id__in=orphan_ids).delete()
        slot_qs.delete()
        return JsonResponse({'status': 'success', 'message': '삭제되었습니다.'})

    raise ActionError('알 수 없는 요청입니다.')


@staff_member_required(login_url='/login/')
def dashboard_redirect_view(request):
    return redirect('academy_admin:schedule_manage')


@staff_member_required(login_url='/login/')
def manage_schedule_view(request):
    """관리자 전용: 시즌별 학원 토탈스케줄 편성 및 교시 시간 유동 설정"""
    payload = _read_payload(request)

    # 시즌이 하나도 없는 최초 접속 때만 기본 시즌을 자동으로 만듭니다.
    if not ScheduleSeason.objects.exists():
        with transaction.atomic():
            if not ScheduleSeason.objects.exists():
                default_season = ScheduleSeason.objects.create(name='기본 시즌 스케줄', is_active=True)
                _ensure_season_periods(default_season)

    seasons = ScheduleSeason.objects.all()
    current_season = _pick_season(request, payload, seasons)
    _ensure_season_periods(current_season)

    if request.method == 'POST':
        return _run_action(_handle_schedule_action, payload, current_season)

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


# ---------------------------------------------------------------------------
# 2. 학생별 수강 배정
# ---------------------------------------------------------------------------
def _handle_enroll_action(payload, current_season, current_student, course_map):
    action = payload.get('action')

    if action == 'enroll':
        subject = str(payload.get('subject', '')).strip()
        teacher_name = str(payload.get('teacher_name', '')).strip()
        class_name = str(payload.get('class_name', '')).strip()

        target_course = course_map.get((subject, teacher_name, class_name))
        if not target_course:
            raise ActionError('토탈스케줄에 존재하지 않는 강좌입니다.')

        if StudentEnrollment.objects.filter(
            student=current_student, season=current_season,
            subject=subject, teacher_name=teacher_name, class_name=class_name
        ).exists():
            raise ActionError('이미 해당 학생에게 배정된 반입니다.')

        occupied = {}
        for enr in StudentEnrollment.objects.filter(student=current_student, season=current_season):
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
                conflicts.append(
                    f"{_day_label(day_idx)}요일 {p_name} — 기존 [{occupied[(day_idx, pid)]}] 수업과 겹침"
                )

        if conflicts:
            return JsonResponse({
                'status': 'conflict',
                'message': "⚠️ 시간표 충돌로 배정할 수 없습니다!\n\n" + "\n".join(conflicts),
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
        deleted, _detail = StudentEnrollment.objects.filter(
            id=_to_int(payload.get('enrollment_id'), '배정'), student=current_student
        ).delete()
        if not deleted:
            raise ActionError('배정 정보를 찾을 수 없습니다. 새로고침 후 다시 시도해 주세요.', status=404)
        return JsonResponse({'status': 'success'})

    raise ActionError('알 수 없는 요청입니다.')


@staff_member_required(login_url='/login/')
def student_enroll_view(request):
    """관리자 전용: 회원 가입한 학생별 수강 반 배정 및 동시간대 충돌 검증"""
    seasons = ScheduleSeason.objects.all()
    payload = _read_payload(request)
    current_season = _pick_season(request, payload, seasons)

    if not current_season:
        return render(request, 'academy_admin/student_enroll.html', {'no_season': True})

    students = list(User.objects.filter(is_staff=False, is_superuser=False).order_by('first_name', 'username'))
    selected_student_id = request.GET.get('student') or request.POST.get('student_id') or payload.get('student_id')
    current_student = None
    if students:
        if selected_student_id:
            current_student = next((u for u in students if str(u.id) == str(selected_student_id)), students[0])
        else:
            current_student = students[0]

    all_slots = list(current_season.class_slots.select_related('period').order_by('day_of_week', 'period__order'))

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
            f"{_day_label(s.day_of_week)} {s.period.name}({s.period.start_time:%H:%M}~{s.period.end_time:%H:%M})"
        )

    available_courses = sorted(course_map.values(), key=lambda x: (x['subject'], x['teacher_name'], x['class_name']))

    if request.method == 'POST':
        if not current_student:
            return JsonResponse({'status': 'error', 'message': '배정할 학생 회원이 없습니다.'}, status=400)
        return _run_action(_handle_enroll_action, payload, current_season, current_student, course_map)

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
