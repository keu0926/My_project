document.addEventListener('DOMContentLoaded', function () {
    const display = document.getElementById('stopwatch-display');
    const btnStart = document.getElementById('btn-timer-start');
    const btnPause = document.getElementById('btn-timer-pause');
    const btnStop = document.getElementById('btn-timer-stop');
    const subjButtons = document.querySelectorAll('#timer-subject-buttons .timer-subj-btn');

    if (!display) return;

    // 오늘 날짜 키로 브라우저에 누적 시간 임시 보존 (새로고침 방지)
    // (상단 todayKey 부분을 아래 두 줄로 교체하면 정확히 밤 12시 자정에 자동 리셋됩니다)
    const tzOffset = new Date().getTimezoneOffset() * 60000;
    const todayKey = 'planner_timer_' + new Date(Date.now() - tzOffset).toISOString().slice(0, 10);

    // 과목별 누적 시간(초 단위) 전역 객체 (나중에 서버 전송 시 활용)
    window.subjectAccumSeconds = {
        '국어': savedData['국어'] || 0,
        '수학': savedData['수학'] || 0,
        '영어': savedData['영어'] || 0,
        '과탐': savedData['과탐'] || 0,
        '사탐': savedData['사탐'] || 0
    };

    let currentSubject = '국어';
    let timerState = 'idle'; // 'idle' | 'running' | 'paused'
    let startTimestamp = 0;  // 시작 버튼 누른 시각(ms)
    let elapsedBeforePause = 0; // 일시정지 전까지 누적된 시간(ms)
    let intervalId = null;

    // 초(sec)를 HH:MM:SS 포맷으로 변환
    function formatHMS(totalSeconds) {
        const hrs = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        return [hrs, mins, secs].map(v => String(v).padStart(2, '0')).join(':');
    }

    // 현재까지 흐른 초(sec) 계산
    function getCurrentElapsedSeconds() {
        if (timerState === 'running') {
            return Math.floor((elapsedBeforePause + (Date.now() - startTimestamp)) / 1000);
        }
        return Math.floor(elapsedBeforePause / 1000);
    }

    // 하단 과목별 누적 시간 및 TOTAL TIME UI 갱신
    function renderAccumulatedTimes() {
        let total = 0;
        Object.keys(window.subjectAccumSeconds).forEach(subj => {
            const sec = window.subjectAccumSeconds[subj];
            total += sec;
            const el = document.getElementById(`accum-${subj}`);
            if (el) el.textContent = formatHMS(sec);
        });
        const totalEl = document.getElementById('accum-total');
        if (totalEl) totalEl.textContent = formatHMS(total);
    }

    // 과목 선택 버튼 제어 (타이머 작동 중에는 변경 불가)
    function setSubjectButtonsDisabled(disabled) {
        subjButtons.forEach(btn => {
            btn.disabled = disabled;
        });
    }

    subjButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (timerState !== 'idle') return;
            subjButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentSubject = btn.dataset.subj;
        });
    });

    // 1. 시작 (또는 재개) 버튼
    btnStart.addEventListener('click', () => {
        if (timerState === 'running') return;

        timerState = 'running';
        startTimestamp = Date.now();
        setSubjectButtonsDisabled(true);

        display.classList.add('running');
        display.classList.remove('paused');

        btnStart.disabled = true;
        btnStart.textContent = '시작';
        btnPause.disabled = false;
        btnStop.disabled = false;

        intervalId = setInterval(() => {
            display.textContent = formatHMS(getCurrentElapsedSeconds());
        }, 250);
    });

    // 2. 잠시 멈춤 버튼
    btnPause.addEventListener('click', () => {
        if (timerState !== 'running') return;

        clearInterval(intervalId);
        elapsedBeforePause += (Date.now() - startTimestamp);
        timerState = 'paused';

        display.classList.remove('running');
        display.classList.add('paused');

        btnStart.disabled = false;
        btnStart.textContent = '계속';
        btnPause.disabled = true;
    });

    // 3. 종료 (리셋 및 과목별 누적 합산) 버튼
    btnStop.addEventListener('click', () => {
        if (timerState === 'idle') return;

        clearInterval(intervalId);
        const sessionSeconds = getCurrentElapsedSeconds();

        // 1초 이상 측정된 경우 해당 과목 누적 시간에 합산
        if (sessionSeconds > 0) {
            window.subjectAccumSeconds[currentSubject] += sessionSeconds;
            localStorage.setItem(todayKey, JSON.stringify(window.subjectAccumSeconds));
            renderAccumulatedTimes();
        }

        // 상태 및 화면 리셋
        timerState = 'idle';
        startTimestamp = 0;
        elapsedBeforePause = 0;

        display.textContent = '00:00:00';
        display.classList.remove('running', 'paused');

        btnStart.disabled = false;
        btnStart.textContent = '시작';
        btnPause.disabled = true;
        btnStop.disabled = true;
        setSubjectButtonsDisabled(false);
    });

    // 초기 누적 시간 표시
    renderAccumulatedTimes();
});

// (planner_timer.js 맨 아래에 추가: 외부에서 전체 초기화 시 타이머도 즉시 0으로 리셋)
    window.resetTimerAll = function () {
        clearInterval(intervalId);
        timerState = 'idle';
        sessionFirstStartTime = 0;
        startTimestamp = 0;
        elapsedBeforePause = 0;

        Object.keys(window.subjectAccumSeconds).forEach(k => {
            window.subjectAccumSeconds[k] = 0;
        });
        localStorage.removeItem(todayKey);
        renderAccumulatedTimes();

        display.textContent = '00:00:00';
        display.classList.remove('running', 'paused');
        btnStart.disabled = false;
        btnStart.textContent = '시작';
        btnPause.disabled = true;
        btnStop.disabled = true;
        setSubjectButtonsDisabled(false);
    };