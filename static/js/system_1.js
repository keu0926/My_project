  // 스크롤을 내려 배너가 화면에 나타나는 순간 애니메이션 실행
  document.addEventListener("DOMContentLoaded", () => {
    const banner = document.getElementById("brandBanner1");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          banner.classList.add("is-visible");
          observer.unobserve(banner); // 한 번 실행 후 유지
        }
      });
    }, { threshold: 0.35 }); // 배너가 화면에 35% 이상 보일 때 작동

    if (banner) observer.observe(banner);
  });


  // 스크롤이 슬로건 섹션에 닿으면 애니메이션 실행
  document.addEventListener("DOMContentLoaded", () => {
    const sloganBanner = document.getElementById("clinicSloganBanner");
    const sloganObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          sloganBanner.classList.add("is-visible");
          sloganObserver.unobserve(sloganBanner);
        }
      });
    }, { threshold: 0.35 });

    if (sloganBanner) sloganObserver.observe(sloganBanner);
  });