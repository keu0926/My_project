document.addEventListener('DOMContentLoaded', function () {
    const paperArea = document.getElementById('todo-paper-area');
    const emptyMsg = document.getElementById('todo-empty-msg');
    const listContainer = document.getElementById('todo-list-container');
    const modalBackdrop = document.getElementById('todo-modal-backdrop');
    const btnCancel = document.getElementById('btn-todo-cancel');
    const btnConfirm = document.getElementById('btn-todo-confirm');

    if (!paperArea) return;

    // 과목 메타 정보
    const subjects = [
        { key: 'kor', name: '국어', badgeClass: 'badge-kor', inputId: 'input-todo-kor' },
        { key: 'math', name: '수학', badgeClass: 'badge-math', inputId: 'input-todo-math' },
        { key: 'eng', name: '영어', badgeClass: 'badge-eng', inputId: 'input-todo-eng' },
        { key: 'sci', name: '과탐', badgeClass: 'badge-sci', inputId: 'input-todo-sci' },
        { key: 'soc', name: '사탐', badgeClass: 'badge-soc', inputId: 'input-todo-soc' }
    ];

    // 과목 이름 -> 뱃지 클래스 (정해진 5과목만 허용)
    const SUBJECT_BADGES = new Map(subjects.map(s => [s.name, s.badgeClass]));

    // HTML 특수문자 이스케이프 (사용자가 입력한 글이 태그로 해석되지 않게 함)
    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // 서버(DB)에서 불러온 할 일 목록을 검증해서 안전한 형태로 정리
    function sanitizeTodoItems(items) {
        if (!Array.isArray(items)) return [];
        const cleaned = [];

        items.forEach(item => {
            if (!item || typeof item !== 'object') return;

            const badgeClass = SUBJECT_BADGES.get(item.subject);
            const text = String(item.text == null ? '' : item.text).trim();
            if (!badgeClass || !text) return;

            const isDone = item.status === 'complete';
            let rate = parseInt(item.rate, 10);
            if (isNaN(rate) || rate < 0) rate = 0;
            if (rate > 100) rate = 100;

            cleaned.push({
                id: cleaned.length + 1,
                subject: item.subject,
                badgeClass: badgeClass,
                text: text,
                status: isDone ? 'complete' : 'incomplete',
                rate: isDone ? 100 : rate
            });
        });

        return cleaned;
    }

    // 현재 등록된 할 일 배열
    window.todoItems = [];

    // 1. 종이 영역 클릭 시 (수정 모드일 때만 입력 모달 열기)
    paperArea.addEventListener('click', function (e) {
        // 라디오 버튼이나 수행률 입력칸을 클릭한 경우에는 모달이 열리지 않도록 예외 처리
        if (e.target.closest('.todo-controls')) return;

        if (window.currentMode !== 'edit') return;
        openTodoModal();
    });

    function openTodoModal() {
        // 기존에 입력된 항목들을 과목별 텍스트창에 복원
        subjects.forEach(sub => {
            const lines = window.todoItems
                .filter(item => item.subject === sub.name)
                .map(item => item.text);
            document.getElementById(sub.inputId).value = lines.join('\n');
        });
        modalBackdrop.classList.add('open');
    }

    btnCancel.addEventListener('click', () => {
        modalBackdrop.classList.remove('open');
    });

    // 2. 확인 버튼 클릭 시 문장 단위로 쪼개어 밑줄 종이에 렌더링
    btnConfirm.addEventListener('click', () => {
        const newItems = [];
        let idCounter = 1;

        subjects.forEach(sub => {
            const rawText = document.getElementById(sub.inputId).value;
            const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            lines.forEach(line => {
                // 이전에 동일 과목+동일 문장이 있었다면 완료/수행률 상태 유지
                const existing = window.todoItems.find(
                    old => old.subject === sub.name && old.text === line
                );
                newItems.push({
                    id: idCounter++,
                    subject: sub.name,
                    badgeClass: sub.badgeClass,
                    text: line,
                    status: existing ? existing.status : 'incomplete', // 기본값: 미완료
                    rate: existing ? existing.rate : 0
                });
            });
        });

        window.todoItems = newItems;
        renderTodoList();
        modalBackdrop.classList.remove('open');
    });

    // 3. 밑줄 친 종이 위에 할 일 목록과 라디오/수행률 칸 그리기
    function renderTodoList() {
        if (window.todoItems.length === 0) {
            emptyMsg.style.display = 'block';
            listContainer.innerHTML = '';
            return;
        }

        emptyMsg.style.display = 'none';
        let html = '';

        window.todoItems.forEach((item, idx) => {
            const isDone = item.status === 'complete';
            const rateValue = isDone ? 100 : (parseInt(item.rate, 10) || 0);
            const badgeClass = SUBJECT_BADGES.get(item.subject) || '';

            html += `
                <div class="todo-row" data-index="${idx}">
                    <div class="todo-left">
                        <span class="todo-subj-badge ${badgeClass}">${escapeHtml(item.subject)}</span>
                        <span class="todo-text ${isDone ? 'done' : ''}" id="todo-text-${idx}">${escapeHtml(item.text)}</span>
                    </div>
                    <div class="todo-controls">
                        <label class="radio-label">
                            <input type="radio" name="todo-status-${idx}" value="incomplete" ${!isDone ? 'checked' : ''} onchange="updateTodoStatus(${idx}, 'incomplete')">
                            미완료
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="todo-status-${idx}" value="complete" ${isDone ? 'checked' : ''} onchange="updateTodoStatus(${idx}, 'complete')">
                            완료
                        </label>
                        <div class="rate-box">
                            <input type="number" class="rate-input" id="todo-rate-${idx}" min="0" max="100" value="${rateValue}" ${isDone ? 'disabled' : ''} oninput="updateTodoRate(${idx}, this.value)">
                            <span>%</span>
                        </div>
                    </div>
                </div>
            `;
        });

        listContainer.innerHTML = html;
    }

    // 서버(DB)에 저장돼 있던 할 일을 화면에 복원 (dashboard.html 에서 호출)
    window.restoreTodoItems = function (items) {
        window.todoItems = sanitizeTodoItems(items);
        renderTodoList();
    };

    // 4. 완료 / 미완료 라디오 버튼 상태 변경 및 100% 비활성화 제어
    window.updateTodoStatus = function (index, status) {
        const item = window.todoItems[index];
        if (!item) return;

        item.status = status;
        const rateInput = document.getElementById(`todo-rate-${index}`);
        const textSpan = document.getElementById(`todo-text-${index}`);

        if (status === 'complete') {
            item.rate = 100;
            rateInput.value = 100;
            rateInput.disabled = true; // 완료 시 입력 비활성화
            textSpan.classList.add('done');
        } else {
            if (item.rate === 100) item.rate = 0;
            rateInput.value = item.rate;
            rateInput.disabled = false; // 미완료 시 직접 퍼센트 입력 가능
            textSpan.classList.remove('done');
        }
    };

    // 5. 미완료 상태에서 수행률(%) 직접 입력 시 값 반영
    window.updateTodoRate = function (index, val) {
        const item = window.todoItems[index];
        if (!item) return;
        let num = parseInt(val, 10);
        if (isNaN(num) || num < 0) num = 0;
        if (num > 100) num = 100;
        item.rate = num;
    };
});