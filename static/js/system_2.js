  document.addEventListener('DOMContentLoaded', () => {
    const triggers = document.querySelectorAll('.rules-section .accordion-trigger');

    triggers.forEach(trigger => {
      trigger.addEventListener('click', () => {
        const currentItem = trigger.closest('.accordion-item');
        const isAlreadyActive = currentItem.classList.contains('active');

        // 열려 있는 다른 아코디언 닫기 (여러 개 동시에 열어두려면 아래 3줄만 지우면 됩니다)
        document.querySelectorAll('.rules-section .accordion-item').forEach(item => {
          item.classList.remove('active');
        });

        // 클릭한 항목 토글
        if (!isAlreadyActive) {
          currentItem.classList.add('active');
        }
      });
    });
  });
