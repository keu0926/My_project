const modal = document.getElementById('myModal');
const modalBody = document.getElementById('modalBody');

const closeBtn = document.getElementById('closeModal');


// 모든 선생님 카드([data-modal])에 이벤트 적용
document.querySelectorAll('[data-modal]').forEach(card => {

    card.addEventListener('click', () => {

        // 카드에 지정된 콘텐츠 ID 가져오기
        const contentId = card.dataset.modal;

        // 해당 콘텐츠 템플릿 찾기
        const template = document.getElementById(contentId);

        if (!template) return;

        // 기존 내용 삭제 후 새로운 내용 삽입
        modalBody.replaceChildren(
            template.content.cloneNode(true)
        );

        // 모달 열기
        if (!modal.open) {
            modal.showModal();
        }

    });

});


// 닫기 버튼
closeBtn.addEventListener('click', () => {
    modal.close();
});


// 모달 바깥쪽 클릭 시 닫기
modal.addEventListener('click', (event) => {

    if (event.target === modal) {
        modal.close();
    }

});