document.addEventListener("DOMContentLoaded", function () {
    const introScreen = document.getElementById("intro-screen");
    if (!introScreen) return;

    // 만약 현재 페이지가 홈이 아니라 서브 페이지라면 인트로를 아예 강제로 제거
    // (서브 페이지에서는 인트로가 보이면 안 되므로 즉시 없앰)
    const isHome = window.location.pathname === '/' || window.location.pathname.includes('home');
    if (!isHome) {
        introScreen.remove();
        return;
    }

    // 현재 방문 중 이미 인트로를 확인했다면 표시하지 않음
    if (sessionStorage.getItem("introVisited") === "true") {
        introScreen.remove();
        return;
    }

    document.body.classList.add("intro-active");

    // 인트로 이미지 클릭 시
    introScreen.addEventListener("click", function () {
        sessionStorage.setItem("introVisited", "true");
        introScreen.classList.add("hide");
        document.body.classList.remove("intro-active");

        setTimeout(function () {
            introScreen.remove();
        }, 1000);
    });
});












const slides = document.querySelectorAll('.slide');
const pagination = document.getElementById('pagination');
let currentIndex = 0;
const totalSlides = slides.length;
let timer = null;

// [초기화] 하단 점 생성
slides.forEach((_, index) => {
    const dot = document.createElement('div');
    dot.classList.add('dot');
    if (index === 0) dot.classList.add('active');
    dot.addEventListener('click', () => {
        goToSlide(index);
        resetTimer();
    });
    pagination.appendChild(dot);
});

const dots = document.querySelectorAll('.dot');

    // [핵심] 슬라이드 클래스 부여 함수 (중앙, 좌, 우 배치)
function updateSlider() {
    slides.forEach((slide, index) => {
    // 모든 클래스 초기화
    slide.classList.remove('active', 'prev', 'next');
        
    // 이전/다음 인덱스 계산 (무한 로테이션을 위한 나머지 연산)
    const prevIndex = (currentIndex - 1 + totalSlides) % totalSlides;
    const nextIndex = (currentIndex + 1) % totalSlides;

    if (index === currentIndex) {
        slide.classList.add('active');
    } else if (index === prevIndex) {
        slide.classList.add('prev');
    } else if (index === nextIndex) {
        slide.classList.add('next');
    }
});

// 점 업데이트
dots.forEach((dot, index) => {
    dot.classList.toggle('active', index === currentIndex);
    });
}

    // 다음 슬라이드로 이동
function nextSlide() {
    currentIndex = (currentIndex + 1) % totalSlides;
    updateSlider();
}

// 특정 슬라이드로 이동
function goToSlide(index) {
    currentIndex = index;
    updateSlider();
}

// 자동 롤링 타이머 설정 (3초)
function startTimer() {
    timer = setInterval(nextSlide, 6000);
}

// 클릭 시 타이머 리셋
function resetTimer() {
    clearInterval(timer);
    startTimer();
}

// 첫 실행
updateSlider();
startTimer();






function smoothScroll(event, targetId) {
	event.preventDefault(); // 기본 순간이동 막기
    
	const targetElement = document.querySelector(targetId);
	if (!targetElement) return;

	// 현재 스크롤 위치와 목적지 위치 계산
	const startPosition = window.pageYOffset || document.documentElement.scrollTop;
	const targetPosition = targetElement.getBoundingClientRect().top + startPosition;
	const distance = targetPosition - startPosition;
    
	// ⏱️ [여기서 조절!] 이동할 총 시간 (밀리초 단위)
	// 1000 = 1초, 1500 = 1.5초 (숫자가 클수록 더 느리고 천천히 부드럽게 이동합니다)
	const duration = 800; 
    
	let startTimestamp = null;

	function step(timestamp) {
		if (!startTimestamp) startTimestamp = timestamp;
		const progress = timestamp - startTimestamp;
      
		// 진행률 계산 (0에서 1까지)
		const progressPercentage = Math.min(progress / duration, 1);
      
		// 🪄 더 부드러운 감속 효과를 주는 수학 공식 (Cubic Easing Out)
		// 처음엔 빠르다가 목적지에 도착할 때 아주 스무스하게 속도가 줄어듭니다.
		const easeOutCubic = 1 - Math.pow(1 - progressPercentage, 3);

		// 스크롤 이동 적용
		window.scrollTo(0, startPosition + distance * easeOutCubic);

		// 목표 시간에 도달할 때까지 프레임 반복 재생
		if (progress < duration) {
			window.requestAnimationFrame(step);
		}
	}

	window.requestAnimationFrame(step);
}







    document.addEventListener("DOMContentLoaded", () => {
      // 위로, 왼쪽에서, 오른쪽에서 오는 모든 요소를 한 번에 선택
      const revealElements = document.querySelectorAll(".reveal-up, .reveal-left, .reveal-right, .reveal-fadein");

      const observerOptions = {
        root: null,
        rootMargin: "0px",
        threshold: 0.15
      };

      const observerCallback = (entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("active");
            observer.unobserve(entry.target);
          }
        });
      };

      const observer = new IntersectionObserver(observerCallback, observerOptions);
      revealElements.forEach(el => observer.observe(el));
    });
    





