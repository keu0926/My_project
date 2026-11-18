document.addEventListener('DOMContentLoaded', function () {
    const tbody = document.getElementById('timetable-body');
    if (!tbody) return;

    // 1. 08:00 ~ 22:00 (08시 행부터 21시 행까지 총 14시간 * 6칸 = 84칸 생성)
    const startHour = 8;
    const endHour = 21; // 21:00 ~ 22:00 구간까지
    let html = '';

    for (let h = startHour; h <= endHour; h++) {
        // 인쇄본처럼 12시간제 표기(8~12, 1~10)를 원하시면 (h > 12 ? h - 12 : h) 사용, 기본은 08~21 표기
        const displayHour = h > 12 ? h - 12 : h;
        const hourCode = String(h).padStart(2, '0');

        html += `<tr>`;
        html += `<td class="hour-cell">${displayHour}</td>`;

        for (let m = 0; m < 60; m += 10) {
            const minCode = String(m).padStart(2, '0');
            const timeStr = `${hourCode}:${minCode}`;
            html += `<td class="tt-slot" data-time="${timeStr}" data-subject="" data-type="" title="${timeStr}"></td>`;
        }
        html += `</tr>`;
    }
    tbody.innerHTML = html;

    // 2. 상태 변수
    window.currentMode = 'edit'; // 'edit'(수정) | 'exec'(실행)
    window.selectedSubject = '국어';
    window.selectedType = 'study'; // 'study'(개별공부-형광) | 'class'(정규수업-빗금)

    let isDragging = false;
    let dragAction = 'paint'; // 'paint' 또는 'erase'

    // 과목별 색상 팔레트
    const neonColors = {
        '국어': 'rgba(255, 235, 59, 0.75)',  // 형광 노랑
        '수학': 'rgba(0, 229, 255, 0.65)',   // 형광 민트/하늘
        '영어': 'rgba(255, 152, 0, 0.65)',   // 형광 주황
        '과탐': 'rgba(105, 240, 174, 0.75)', // 형광 연두
        '사탐': 'rgba(255, 128, 171, 0.75)'  // 형광 핑크
    };

    const stripeBaseColors = {
        '국어': '#fff59d',
        '수학': '#b2ebf2',
        '영어': '#ffe0b2',
        '과탐': '#c8e6c9',
        '사탐': '#f8bbd0'
    };

    // 과목별 실제 공부 시간 표시용 진한 테두리 색상
    const actualBorderColors = {
        '국어': '#f57f17', // 진한 노랑/호박색
        '수학': '#00838f', // 진한 청록/하늘색
        '영어': '#e65100', // 진한 주황색
        '과탐': '#1b5e20', // 진한 초록색
        '사탐': '#ad1457'  // 진한 핑크/자주색
    };

    // 단일 슬롯에 진한 안쪽 테두리 적용 함수
    window.renderActualBorder = function(cell, subject) {
        if (!cell) return;
        if (subject && actualBorderColors[subject]) {
            cell.dataset.actual = subject;
            cell.style.boxShadow = `inset 0 0 0 2.5px ${actualBorderColors[subject]}`;
        } else {
            cell.dataset.actual = '';
            cell.style.boxShadow = 'none';
        }
    };

    // 타이머 종료 시 시작~종료 시각을 10분 단위로 반올림하여 타임테이블에 테두리 표시
    window.markActualStudyTime = function(startMs, endMs, subject) {
        if (!startMs || !endMs || endMs <= startMs) return;

        const TEN_MIN = 10 * 60 * 1000;
        // 시작 시각과 종료 시각을 가장 가까운 10분 단위로 반올림
        let roundedStart = Math.round(startMs / TEN_MIN) * TEN_MIN;
        let roundedEnd = Math.round(endMs / TEN_MIN) * TEN_MIN;

        // 만약 5분 이상 공부했는데 시작과 끝이 같은 10분선으로 반올림된 경우 최소 1칸(10분) 보장
        if (roundedStart === roundedEnd && (endMs - startMs) >= 5 * 60 * 1000) {
            roundedEnd = roundedStart + TEN_MIN;
        }

        for (let t = roundedStart; t < roundedEnd; t += TEN_MIN) {
            const d = new Date(t);
            const h = d.getHours();
            const m = d.getMinutes();

            // 타임테이블 범위(08:00 ~ 21:50) 내에 있을 때만 표시
            if (h >= 8 && h <= 21) {
                const timeStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
                const cell = tbody.querySelector(`.tt-slot[data-time="${timeStr}"]`);
                if (cell) {
                    window.renderActualBorder(cell, subject);
                }
            }
        }
    };

    function applySlot(cell, action) {
        if (window.currentMode === 'exec') {
            // 실행 모드일 때는 이미 칠해진 칸만 완료 체크 토글
            if (cell.dataset.subject) {
                cell.classList.toggle('checked');
            }
            return;
        }

        // 수정 모드일 때 색칠 또는 지우기
        if (action === 'erase') {
            cell.dataset.subject = '';
            cell.dataset.type = '';
            cell.style.background = '#ffffff';
            cell.classList.remove('checked');
        } else {
            cell.dataset.subject = window.selectedSubject;
            cell.dataset.type = window.selectedType;

            if (window.selectedType === 'study') {
                // 개별 공부: 형광색 단색 채우기
                cell.style.background = neonColors[window.selectedSubject] || '#fffa65';
            } else {
                // 정규 수업: 과목 색상이 들어간 빗금 무늬
                const base = stripeBaseColors[window.selectedSubject] || '#e0e0e0';
                cell.style.background = `repeating-linear-gradient(45deg, ${base}, ${base} 4px, #ffffff 4px, #ffffff 8px)`;
            }
        }
    }

    // 3. 마우스 및 터치 드래그 이벤트 연결
    const slots = tbody.querySelectorAll('.tt-slot');

    slots.forEach(slot => {
        slot.addEventListener('mousedown', (e) => {
            e.preventDefault();
            isDragging = true;
            // 이미 같은 과목+같은 타입이 칠해져 있으면 드래그하는 동안 지우기 모드로 작동
            if (slot.dataset.subject === window.selectedSubject && slot.dataset.type === window.selectedType) {
                dragAction = 'erase';
            } else {
                dragAction = 'paint';
            }
            applySlot(slot, dragAction);
        });

        slot.addEventListener('mouseenter', () => {
            if (!isDragging || window.currentMode !== 'edit') return;
            applySlot(slot, dragAction);
        });
    });

    // 모바일 손가락 터치 드래그 지원
    tbody.addEventListener('touchstart', (e) => {
        const touch = e.touches[0];
        const target = document.elementFromPoint(touch.clientX, touch.clientY);
        if (target && target.classList.contains('tt-slot')) {
            e.preventDefault();
            isDragging = true;
            if (target.dataset.subject === window.selectedSubject && target.dataset.type === window.selectedType) {
                dragAction = 'erase';
            } else {
                dragAction = 'paint';
            }
            applySlot(target, dragAction);
        }
    }, { passive: false });

    tbody.addEventListener('touchmove', (e) => {
        if (!isDragging || window.currentMode !== 'edit') return;
        e.preventDefault();
        const touch = e.touches[0];
        const target = document.elementFromPoint(touch.clientX, touch.clientY);
        if (target && target.classList.contains('tt-slot')) {
            applySlot(target, dragAction);
        }
    }, { passive: false });

    document.addEventListener('mouseup', () => { isDragging = false; });
    document.addEventListener('touchend', () => { isDragging = false; });

    // 외부 버튼 연동 함수
    window.selectTool = function(subject, type) {
        if (subject) window.selectedSubject = subject;
        if (type) window.selectedType = type;
    };

    window.setPlannerMode = function(mode) {
        window.currentMode = mode;
        const badge = document.getElementById('current-mode-label');
        const btnExec = document.getElementById('btn-mode-exec');
        const btnEdit = document.getElementById('btn-mode-edit');

        if (badge) {
            badge.textContent = (mode === 'edit') ? '수정 모드' : '실행 모드';
            badge.style.background = (mode === 'edit') ? '#fff3e0' : '#e8f2ff';
            badge.style.color = (mode === 'edit') ? '#ff9500' : '#0071e3';
        }
        if (btnExec && btnEdit) {
            btnExec.classList.toggle('active', mode === 'exec');
            btnEdit.classList.toggle('active', mode === 'edit');
        }
    };
});