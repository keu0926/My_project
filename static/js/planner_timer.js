// 서버에서 Django 템플릿을 통해 전달받은 저장된 타이머 데이터를 안전하게 파싱
const savedData = JSON.parse(
    (document.getElementById('server-timer-data') || document.getElementById('saved-timer-data'))?.textContent || '{}'
);

document.addEventListener('DOMContentLoaded', function () {
    const display = document.getElementById('stopwatch-display');
    const btnStart = document.getElementById('btn-timer-start');
    const btnPause = document.getElementById('btn-timer-pause');
    const btnStop = document.getElementById('btn-timer-stop');
    const subjButtons = document.querySelectorAll('#timer-subject-buttons .timer-subj-btn');

    if (!display) return;

    const tzOffset = new Date().getTimezoneOffset() * 60000;
    const todayKey = 'planner_timer_' + new Date(Date.now() - tzOffset).toISOString().slice(0, 10);
    const stateKey = 'planner_timer_state_' + todayKey;

    const localSaved = JSON.parse(localStorage.getItem(todayKey));
    window.subjectAccumSeconds = {
        '국어': (localSaved && localSaved['국어'] !== undefined) ? localSaved['국어'] : (savedData['국어'] || 0),
        '수학': (localSaved && localSaved['수학'] !== undefined) ? localSaved['수학'] : (savedData['수학'] || 0),
        '영어': (localSaved && localSaved['영어'] !== undefined) ? localSaved['영어'] : (savedData['영어'] || 0),
        '과탐': (localSaved && localSaved['과탐'] !== undefined) ? localSaved['과탐'] : (savedData['과탐'] || 0),
        '사탐': (localSaved && localSaved['사탐'] !== undefined) ? localSaved['사탐'] : (savedData['사탐'] || 0)
    };

    let currentSubject = '국어';
    let timerState = 'idle'; // 'idle' | 'running' | 'paused'
    let sessionFirstStartTime = 0; // 이번 타이머 세션의 최초 시작 시각(ms)
    let startTimestamp = 0;
    let elapsedBeforePause = 0;
    let intervalId = null;

    function formatHMS(totalSeconds) {
        const hrs = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        return [hrs, mins, secs].map(v => String(v).padStart(2, '0')).join(':');
    }

    function getCurrentElapsedSeconds() {
        if (timerState === 'running') {
            return Math.floor((elapsedBeforePause + (Date.now() - startTimestamp)) / 1000);
        }
        return Math.floor(elapsedBeforePause / 1000);
    }

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

    function saveTimerStateToLocal() {
        const stateData = {
            timerState,
            sessionFirstStartTime,
            startTimestamp,
            elapsedBeforePause,
            currentSubject
        };
        localStorage.setItem(stateKey, JSON.stringify(stateData));
    }

    // 1. 시작 (또는 재개) 버튼
    btnStart.addEventListener('click', () => {
        if (timerState === 'running') return;

        // 처음 시작할 때만 최초 시작 시각 기록
        if (timerState === 'idle') {
            sessionFirstStartTime = Date.now();
        }
        timerState = 'running';
        startTimestamp = Date.now();
        setSubjectButtonsDisabled(true);

        display.classList.add('running');
        display.classList.remove('paused');

        btnStart.disabled = true;
        btnStart.textContent = '시작';
        btnPause.disabled = false;
        btnStop.disabled = false;

        saveTimerStateToLocal();

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

        saveTimerStateToLocal();
    });

    // 3. 종료 (리셋, 누적 합산 및 타임테이블 테두리 표시) 버튼
    btnStop.addEventListener('click', () => {
        if (timerState === 'idle') return;

        clearInterval(intervalId);
        const sessionSeconds = getCurrentElapsedSeconds();
        const endTimestamp = Date.now();

        if (sessionSeconds > 0) {
            window.subjectAccumSeconds[currentSubject] += sessionSeconds;
            localStorage.setItem(todayKey, JSON.stringify(window.subjectAccumSeconds));
            renderAccumulatedTimes();

            // 타임테이블에 10분 단위 반올림으로 진한 테두리 그리기
            if (typeof window.markActualStudyTime === 'function') {
                const startMs = sessionFirstStartTime || (endTimestamp - sessionSeconds * 1000);
                window.markActualStudyTime(startMs, endTimestamp, currentSubject);
            }
        }

        timerState = 'idle';
        sessionFirstStartTime = 0;
        startTimestamp = 0;
        elapsedBeforePause = 0;
        localStorage.removeItem(stateKey);

        display.textContent = '00:00:00';
        display.classList.remove('running', 'paused');

        btnStart.disabled = false;
        btnStart.textContent = '시작';
        btnPause.disabled = true;
        btnStop.disabled = true;
        setSubjectButtonsDisabled(false);
    });

    // 페이지 이동 후 복귀 시 상태 복원
    const savedState = JSON.parse(localStorage.getItem(stateKey));
    if (savedState) {
        timerState = savedState.timerState;
        sessionFirstStartTime = savedState.sessionFirstStartTime || savedState.startTimestamp || 0;
        startTimestamp = savedState.startTimestamp || 0;
        elapsedBeforePause = savedState.elapsedBeforePause || 0;
        currentSubject = savedState.currentSubject || '국어';

        subjButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.subj === currentSubject);
        });

        if (timerState === 'running' || timerState === 'paused') {
            display.textContent = formatHMS(getCurrentElapsedSeconds());
            setSubjectButtonsDisabled(true);
            btnStop.disabled = false;

            if (timerState === 'running') {
                display.classList.add('running');
                btnStart.disabled = true;
                btnPause.disabled = false;
                btnStart.textContent = '시작';
                intervalId = setInterval(() => {
                    display.textContent = formatHMS(getCurrentElapsedSeconds());
                }, 250);
            } else {
                display.classList.add('paused');
                btnStart.disabled = false;
                btnPause.disabled = true;
                btnStart.textContent = '계속';
            }
        }
    }

    // 외부에서 전체 초기화 시 타이머도 즉시 0으로 리셋
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
        localStorage.removeItem(stateKey);
        renderAccumulatedTimes();

        display.textContent = '00:00:00';
        display.classList.remove('running', 'paused');
        btnStart.disabled = false;
        btnStart.textContent = '시작';
        btnPause.disabled = true;
        btnStop.disabled = true;
        setSubjectButtonsDisabled(false);
    };

    renderAccumulatedTimes();
});