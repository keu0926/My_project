  // ==========================================
  // [여기서만 수정하세요] 합격증 이미지 경로 목록
  // ==========================================
  // 따옴표("") 안에 사진 파일명이나 주소를 적으면 됩니다. (비워두면 기본 아이콘 표시)
  const certImages = [
    "/static/images/합격증1.jpg", 
    "/static/images/합격증2.jpg", 
    "/static/images/합격증3.jpg",
    "/static/images/합격증4.jpg",
    "/static/images/합격증5.jpg",
    "/static/images/합격증6.jpg",
    "/static/images/합격증7.jpg",
    "/static/images/합격증8.jpg",
    "/static/images/합격증9.jpg",
    "/static/images/합격증10.jpg",
    "/static/images/합격증11.jpg",
    "/static/images/합격증12.jpg",
    "/static/images/합격증13.jpg",
    "/static/images/합격증14.jpg",
    "/static/images/합격증15.jpg",
    "/static/images/합격증16.jpg",
    "/static/images/합격증17.jpg",
    "/static/images/합격증18.jpg",
    "/static/images/합격증19.jpg",
    "/static/images/합격증20.jpg",
    "/static/images/합격증21.jpg",
    "/static/images/합격증22.jpg",
    "/static/images/합격증23.jpg",
    "/static/images/합격증24.jpg",
    "/static/images/합격증25.jpg",
    "/static/images/합격증26.jpg",
    "/static/images/합격증27.jpg",
    "/static/images/합격증28.jpg",
    "/static/images/합격증29.jpg",
    "/static/images/합격증30.jpg",
    "/static/images/합격증31.jpg",
    "/static/images/합격증32.jpg",
    "/static/images/합격증33.jpg",
    "/static/images/합격증34.jpg",
    "/static/images/합격증35.jpg",
    "/static/images/합격증36.jpg",
    "/static/images/합격증37.jpg",
    "/static/images/합격증38.jpg",
    "/static/images/합격증39.jpg",
    "/static/images/합격증40.jpg",
    "/static/images/합격증41.jpg",
    "/static/images/합격증42.jpg",
    "/static/images/합격증43.jpg",
    "/static/images/합격증44.jpg",
    "/static/images/합격증45.jpg",
    "/static/images/합격증46.jpg",
    "/static/images/합격증47.jpg",
    "/static/images/합격증48.jpg",
    "/static/images/합격증49.jpg",
    "/static/images/합격증50.jpg",
    "/static/images/합격증51.jpg",
    "/static/images/합격증52.jpg",
    "/static/images/합격증53.jpg",
    "/static/images/합격증54.jpg",
    "/static/images/합격증55.jpg",
    "/static/images/합격증56.jpg",
    "/static/images/합격증57.jpg",
    "/static/images/합격증58.jpg",
    "/static/images/합격증59.jpg",
    "/static/images/합격증60.jpg",
    "/static/images/합격증61.jpg",
    "/static/images/합격증62.jpg",
    "/static/images/합격증63.jpg",
    "/static/images/합격증64.jpg",
    "/static/images/합격증65.jpg",
    "/static/images/합격증66.jpg",
    "/static/images/합격증67.jpg",
    "/static/images/합격증68.jpg",
    "/static/images/합격증69.jpg",
    "/static/images/합격증70.jpg",
    "/static/images/합격증71.jpg",
    "/static/images/합격증72.jpg",
    "/static/images/합격증73.jpg",
    "/static/images/합격증74.jpg",
    "/static/images/합격증75.jpg",
    "/static/images/합격증76.jpg",
    "/static/images/합격증77.jpg",
    "/static/images/합격증78.jpg",
    "/static/images/합격증79.jpg",
    "/static/images/합격증80.jpg",
    "/static/images/합격증81.jpg",
    "/static/images/합격증82.jpg",
    "/static/images/합격증83.jpg",
    "/static/images/합격증84.jpg",
    "/static/images/합격증85.jpg",
    "/static/images/합격증86.jpg",
    "/static/images/합격증87.jpg",
    "/static/images/합격증88.jpg",
    "/static/images/합격증89.jpg",
    "/static/images/합격증90.jpg",
    "/static/images/합격증91.jpg",
    "/static/images/합격증92.jpg",
    "/static/images/합격증93.jpg"
  ];

  const certGrid = document.getElementById('certGrid');
  const loadMoreBtn = document.getElementById('loadMoreBtn');
  const btnText = document.getElementById('btnText');
  const certModal = document.getElementById('certModal');
    document.body.appendChild(certModal);

  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalImageWrap = document.getElementById('modalImageWrap');

  const initialCount = 8; // 4열 × 2줄 = 8개
  const stepCount = 8;    // 클릭당 2줄(8개) 추가
  let visibleCount = initialCount;

  const placeholderHTML = `
    <div class="placeholder-box">
      <svg class="placeholder-icon" viewBox="0 0 24 24">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <polyline points="9 15 11 17 15 13"></polyline>
      </svg>
      <span class="placeholder-text">CERTIFICATE</span>
    </div>
  `;

  function openModal(imgSrc, index) {
    modalImageWrap.innerHTML = imgSrc 
      ? `<img src="${imgSrc}" alt="합격증 ${index + 1}">` 
      : placeholderHTML;
    certModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    certModal.classList.remove('open');
    document.body.style.overflow = '';
  }

   function createCards() {
    certGrid.innerHTML = '';
    certImages.forEach((imgSrc, index) => {
      const item = document.createElement('div');
      item.className = 'cert-item';
      item.style.display = index < visibleCount ? 'block' : 'none';

      const imgContent = imgSrc 
        ? `<img src="${imgSrc}" alt="합격증 ${index + 1}">` 
        : placeholderHTML;

      item.innerHTML = `
        <div class="card-image-box">${imgContent}</div>
        <div class="open-btn">
          <svg viewBox="0 0 24 24">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </div>
      `;

      item.addEventListener('click', () => openModal(imgSrc, index));
      certGrid.appendChild(item);
    });
    updateButtonState();
  }

  function updateButtonState() {
    if (certImages.length <= initialCount) {
      loadMoreBtn.style.display = 'none';
      return;
    }
    if (visibleCount >= certImages.length) {
      btnText.textContent = '접기';
      loadMoreBtn.classList.add('all-shown');
    } else {
      btnText.textContent = '합격증 더 보기';
      loadMoreBtn.classList.remove('all-shown');
    }
  }

  loadMoreBtn.addEventListener('click', () => {
    const allItems = document.querySelectorAll('#certGrid .cert-item');
    if (visibleCount >= certImages.length) {
      visibleCount = initialCount;
      certGrid.scrollIntoView({ behavior: 'smooth' });
    } else {
      visibleCount += stepCount;
    }
    allItems.forEach((item, index) => {
      item.style.display = index < visibleCount ? 'block' : 'none';
    });
    updateButtonState();
  });

  modalCloseBtn.addEventListener('click', closeModal);
  certModal.addEventListener('click', (e) => { if (e.target === certModal) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && certModal.classList.contains('open')) closeModal(); });

  createCards();








    // ==========================================
  // [여기서만 수정하세요] 수강 후기 데이터 목록
  // ==========================================
  // quote: 한 줄 후기 내용 (따옴표는 자동으로 붙습니다)
  // info: 수강생 구분 (예: "국어 수강생 · 재수")
  const reviewData = [
    // --- 첫 번째 화면 (1~3번) ---
    { quote: "공부하는 방법부터 달라졌습니다.", info: "종합반 수강생 · 재수" },
    { quote: "혼자였다면 해내지 못했을 것 같아요.", info: "탐구 수강생 · 재수" },
    { quote: "매일의 작은 변화가 결국 결과를 만들었습니다.", info: "종합반 수강생 · 재수" },
    
    // --- 두 번째 화면 (4~6번) ---
    { quote: "막막했던 국어 지문이 이제는 구조로 보입니다.", info: "주말반 수강생 · 고3" },
    { quote: "질문할 때마다 핵심을 짚어주셔서 시간이 단축됐어요.", info: "탐구 수강생 · 재수" },
    { quote: "흔들릴 때마다 잡아주신 덕분에 끝까지 완주했습니다.", info: "종합반 수강생 · 반수" },
    
    // 후기를 더 추가하려면 쉼표(,)를 찍고 아래처럼 3개 단위로 추가하세요.
    // ,{ quote: "새로운 후기 내용입니다.", info: "영어 수강생 · 고3" }
        // --- 세 번째 화면 (7~9번) ---
    { quote: "약점만 정확히 짚어주는 관리 덕분에 성적이 수직 상승했습니다.", info: "종합반 수강생 · 반수" },
    { quote: "기출을 분석하는 눈이 트이니 어떤 낯선 문제도 두렵지 않았어요.", info: "종합반 수강생 · 재수" },
    { quote: "체계적인 학습 루틴이 잡히면서 수험 생활 내내 흔들리지 않았습니다.", info: "종합반 수강생 · 재수" }


  ];

  // ==========================================
  // 자동 위로 슬라이드 동작 코드
  // ==========================================
  const viewport = document.getElementById('reviewsViewport');
  const track = document.getElementById('reviewsTrack');
  const dotsContainer = document.getElementById('reviewsDots');
  const reviewsSection = document.getElementById('reviewsSection');

  const itemsPerPage = 3;      // 한 화면에 보여줄 후기 개수 (3개)
  const slideInterval = 4000;  // 자동 슬라이드 넘어가는 시간 (4000 = 4초)
  let currentPage = 0;
  let totalPages = Math.ceil(reviewData.length / itemsPerPage);
  let autoSlideTimer;

  // 1. 데이터를 3개씩 묶어서 페이지(슬라이드) 생성
  function initReviews() {
    track.innerHTML = '';
    dotsContainer.innerHTML = '';
    const totalCountStr = String(reviewData.length).padStart(2, '0');

    for (let p = 0; p < totalPages; p++) {
      const pageDiv = document.createElement('div');
      pageDiv.className = 'review-page';

      const slice = reviewData.slice(p * itemsPerPage, (p + 1) * itemsPerPage);
      slice.forEach((item, idx) => {
        const globalIndex = p * itemsPerPage + idx + 1;
        const currentNumStr = String(globalIndex).padStart(2, '0');

        const itemDiv = document.createElement('div');
        itemDiv.className = 'review-item';
        itemDiv.innerHTML = `
          <div class="review-quote">"${item.quote}"</div>
          <div class="review-meta">
            <span>${item.info}</span>
            <span class="review-num">${currentNumStr} / ${totalCountStr}</span>
          </div>
        `;
        pageDiv.appendChild(itemDiv);
      });

      track.appendChild(pageDiv);

      // 하단 인디케이터 바 생성
      const dot = document.createElement('button');
      dot.className = p === 0 ? 'dot-btn active' : 'dot-btn';
      dot.setAttribute('aria-label', `${p + 1}번째 후기 묶음 보기`);
      dot.addEventListener('click', () => {
        goToPage(p);
        resetTimer();
      });
      dotsContainer.appendChild(dot);
    }

    // 페이지 높이를 첫 번째 슬라이드 높이에 딱 맞게 고정
    updateViewportHeight();
  }

  // 2. 창문 높이를 정확히 계산해서 다음 줄이 살짝 비치지 않게 방지
  function updateViewportHeight() {
    const pages = document.querySelectorAll('.review-page');
    if (pages.length > 0) {
      viewport.style.height = pages[currentPage].offsetHeight + 'px';
    }
  }

  // 3. 특정 페이지로 부드럽게 위로 이동
  function goToPage(pageIndex) {
    currentPage = pageIndex;
    const pages = document.querySelectorAll('.review-page');
    const offset = pages[currentPage].offsetTop;
    
    track.style.transform = `translateY(-${offset}px)`;
    updateViewportHeight();

    // 인디케이터 활성화 상태 업데이트
    const dots = document.querySelectorAll('.dot-btn');
    dots.forEach((dot, idx) => {
      dot.classList.toggle('active', idx === currentPage);
    });
  }

  // 4. 다음 페이지로 이동 (끝에 도달하면 자연스럽게 1페이지로 복귀)
  function nextPage() {
    const next = (currentPage + 1) % totalPages;
    goToPage(next);
  }

  // 5. 자동 재생 및 일시정지 제어
  function startTimer() {
    if (totalPages <= 1) return;
    autoSlideTimer = setInterval(nextPage, slideInterval);
  }

  function stopTimer() {
    clearInterval(autoSlideTimer);
  }

  function resetTimer() {
    stopTimer();
    startTimer();
  }

  // 마우스를 올리면 읽기 편하도록 자동 슬라이드 일시정지
  reviewsSection.addEventListener('mouseenter', stopTimer);
  reviewsSection.addEventListener('mouseleave', startTimer);
  window.addEventListener('resize', () => goToPage(currentPage));

  // 초기 실행
  initReviews();
  startTimer();