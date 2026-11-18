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

if (slides.length > 0 && pagination) {
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
            slide.classList.remove('active', 'prev', 'next');

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

        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }

    // 다음 / 이전 슬라이드로 이동
    function nextSlide() {
        currentIndex = (currentIndex + 1) % totalSlides;
        updateSlider();
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateSlider();
    }

    function goToSlide(index) {
        currentIndex = index;
        updateSlider();
    }

    // 자동 롤링 타이머 설정 (6초)
    function startTimer() {
        timer = setInterval(nextSlide, 6000);
    }

    function resetTimer() {
        clearInterval(timer);
        startTimer();
    }

    // ★ 모바일 터치 스와이프 & PC 마우스 드래그 통합 처리
    //   - 손가락이 40px 이상 움직이는 순간 바로 슬라이드를 넘깁니다. (touchend를 기다리지 않음)
    //   - 카카오톡 같은 인앱 브라우저에서 touchend 대신 touchcancel이 오더라도 동작하도록 함께 처리합니다.
    //   - 좌표는 screenX 대신 clientX/clientY를 사용합니다.
    const sliderContainer = slides[0].parentElement;
    const SWIPE_THRESHOLD = 40;
    let startX = 0;
    let startY = 0;
    let lastX = 0;
    let lastY = 0;
    let isTouching = false;
    let isDragging = false;
    let isSwiped = false;

    function trySwipe(x, y) {
        if (isSwiped) return;

        const diffX = startX - x;
        const diffY = startY - y;

        // 상하 스크롤보다 좌우 이동폭이 크고, 40px 이상 움직였을 때만 슬라이드 전환
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > SWIPE_THRESHOLD) {
            isSwiped = true;
            if (diffX > 0) {
                nextSlide(); // 왼쪽으로 끌었을 때 -> 다음 슬라이드
            } else {
                prevSlide(); // 오른쪽으로 끌었을 때 -> 이전 슬라이드
            }
            resetTimer();
        }
    }

    // 1) 모바일/태블릿 터치 이벤트
    sliderContainer.addEventListener('touchstart', (e) => {
        const t = e.touches[0];
        startX = lastX = t.clientX;
        startY = lastY = t.clientY;
        isSwiped = false;
        isTouching = true;
    }, { passive: true });

    sliderContainer.addEventListener('touchmove', (e) => {
        if (!isTouching) return;
        const t = e.touches[0];
        lastX = t.clientX;
        lastY = t.clientY;
        trySwipe(lastX, lastY);
    }, { passive: true });

    function endTouch(e) {
        if (!isTouching) return;
        isTouching = false;
        const t = e.changedTouches && e.changedTouches[0];
        trySwipe(t ? t.clientX : lastX, t ? t.clientY : lastY);
    }

    sliderContainer.addEventListener('touchend', endTouch, { passive: true });
    sliderContainer.addEventListener('touchcancel', endTouch, { passive: true });

    // 2) PC 마우스 드래그 이벤트
    sliderContainer.addEventListener('mousedown', (e) => {
        isDragging = true;
        isSwiped = false;
        startX = e.clientX;
        startY = e.clientY;
    });

    window.addEventListener('mouseup', (e) => {
        if (!isDragging) return;
        isDragging = false;
        trySwipe(e.clientX, e.clientY);
    });

    // 마우스로 배너 내부 이미지를 끌 때 기본 고스트 이미지 드래그 방지
    sliderContainer.addEventListener('dragstart', (e) => {
        e.preventDefault();
    });

    // 드래그해서 넘겼을 때 배너 안의 링크(<a>)가 실수로 클릭되는 현상 방지
    sliderContainer.addEventListener('click', (e) => {
        if (isSwiped) {
            e.preventDefault();
            e.stopPropagation();
            isSwiped = false;
        }
    }, true);

    // 첫 실행
    updateSlider();
    startTimer();
}





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
    

    // ==========================================
// 태블릿/모바일 상단 메뉴 터치 토글 처리
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    // 사이트의 드롭다운 메뉴 클래스명에 맞춰 선택자를 확인해 주세요 (예: .dropdown, .nav-item-dropdown 등)
    const dropdowns = document.querySelectorAll('.dropdown, .nav-item-dropdown, .dropdown-menu');

    dropdowns.forEach(dropdown => {
        const toggleBtn = dropdown.querySelector('a, .dropdown-toggle');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function (e) {
                // 모바일/태블릿에서 상위 메뉴를 터치했을 때 바로 링크로 이동하지 않고 메뉴를 펼치게 하려면 아래 주석을 해제하세요
                // e.preventDefault();
                
                // 다른 열려있는 메뉴들은 닫고 현재 메뉴만 토글
                dropdowns.forEach(item => {
                    if (item !== dropdown) item.classList.remove('active');
                });
                
                dropdown.classList.toggle('active');
            });
        }
    });

    // 화면의 다른 곳을 터치하면 열려있던 메뉴가 닫히도록 처리
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.dropdown, .nav-item-dropdown, .dropdown-menu')) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
});