document.addEventListener("DOMContentLoaded", function () {

    /* ================================
       갤러리 이미지 경로 및 데이터
    ================================= */

    const galleryData = {

        classroom: {
            title: "소수정예 특화 강의실",
            photos: [
                {src: "/static/images/lecture_room_1.jpg", caption: "1관 강의실"},
                {src: "/static/images/lecture_room_2.jpg", caption: "1관 강의실"},
                {src: "/static/images/lecture_room_3.jpg", caption: "1관 강의실"},
                {src: "/static/images/lecture_room_4.jpg", caption: "1관 강의실"},
                {src: "/static/images/lecture_room_5.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_6.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_7.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_8.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_9.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_10.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_11.jpg", caption: "2관 강의실"},
                {src: "/static/images/lecture_room_12.jpg", caption: "2관 강의실"}
            ]
        },

        study: {
            title: "파티션 자습실",
            photos: [
                {src: "/static/images/study_room_1.jpg", caption: "개인별 독립 학습 공간"}
            ]
        },

        study2: {
            title: "개방형 자습실",
            photos: [
                {src: "/static/images/study_room_2.jpg", caption: "개방형 개인 자습 공간"}
            ]
        },

        desk: {
            title: "로비 및 안내 데스크",
            photos: [
                {src: "/static/images/lobby_desk_1.jpg", caption: "학원 로비 및 안내 데스크"}
            ]
        },

        exterior: {
            title: "학원 전경",
            photos: [
                {src: "/static/images/academy_exterior_1.jpg", caption: "대치플투스 학원 전경"}
            ]
        }

    };

    /* 아래부터 기존 갤러리 기능 코드 */

    const modal = document.getElementById("photoModal");

    const mainPhoto = document.getElementById("mainPhoto");
    const modalTitle = document.getElementById("modalTitle");
    const photoCounter = document.getElementById("photoCounter");
    const photoCaption = document.getElementById("photoCaption");
    const thumbnails = document.getElementById("thumbnails");

    const closeBtn = modal.querySelector(".close-btn");
    const prevBtn = modal.querySelector(".prev");
    const nextBtn = modal.querySelector(".next");

    let currentGallery = [];
    let currentIndex = 0;


    function showPhoto(index) {

        currentIndex =
            (index + currentGallery.length) % currentGallery.length;

        const photo = currentGallery[currentIndex];

        mainPhoto.src = photo.src;
        mainPhoto.alt = photo.caption || "";

        photoCaption.textContent = photo.caption || "";

        photoCounter.textContent =
            String(currentIndex + 1).padStart(2, "0") +
            " / " +
            String(currentGallery.length).padStart(2, "0");

        renderThumbnails();
    }


    function renderThumbnails() {

        thumbnails.innerHTML = "";

        currentGallery.forEach(function (photo, index) {

            const thumb = document.createElement("button");

            thumb.type = "button";
            thumb.className =
                "thumb" + (index === currentIndex ? " active" : "");

            const img = document.createElement("img");

            img.src = photo.src;
            img.alt = "";

            thumb.appendChild(img);

            thumb.addEventListener("click", function () {
                showPhoto(index);
            });

            thumbnails.appendChild(thumb);

        });
    }


    function openGallery(key) {

        const gallery = galleryData[key];

        if (!gallery || !gallery.photos.length) return;

        currentGallery = gallery.photos;
        currentIndex = 0;

        modalTitle.textContent = gallery.title;

        showPhoto(0);

        if (!modal.open) {
            modal.showModal();
        }

        closeBtn.focus();
    }


    function closeGallery() {
        if (modal.open) modal.close();
    }


    document.addEventListener("click", function (event) {

        const trigger = event.target.closest("[data-gallery]");

        if (!trigger) return;

        event.preventDefault();

        openGallery(trigger.dataset.gallery);

    });


    prevBtn.addEventListener("click", function () {
        showPhoto(currentIndex - 1);
    });

    nextBtn.addEventListener("click", function () {
        showPhoto(currentIndex + 1);
    });

    closeBtn.addEventListener("click", closeGallery);


    modal.addEventListener("click", function (event) {
        if (event.target === modal) closeGallery();
    });


    document.addEventListener("keydown", function (event) {

        if (!modal.open) return;

        if (event.key === "ArrowLeft") {
            showPhoto(currentIndex - 1);
        }

        if (event.key === "ArrowRight") {
            showPhoto(currentIndex + 1);
        }

    });

});

