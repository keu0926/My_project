window.createAcademyMap = function () {

    const mapContainer = document.getElementById("daechi-kakao-map");

    if (!mapContainer) {
        console.error("지도 영역을 찾을 수 없습니다.");
        return;
    }

    const academyPosition = new kakao.maps.LatLng(
        37.502845,
        127.054365
    );

    const map = new kakao.maps.Map(mapContainer, {
        center: academyPosition,
        level: 3
    });

    const marker = new kakao.maps.Marker({
        position: academyPosition
    });

    marker.setMap(map);

    window.addEventListener("resize", function () {
        map.relayout();
        map.setCenter(academyPosition);
    });
};