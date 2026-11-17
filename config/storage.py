import os

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import StaticFilesStorage


class VersionedStaticFilesStorage(StaticFilesStorage):
    """
    {% static %} 로 만들어지는 모든 주소 끝에 ?v=<파일 수정시간> 을 붙입니다.

    파일 내용이 바뀌면 주소도 바뀌므로, 카카오톡/인스타그램 같은 인앱 브라우저나
    사파리가 예전 CSS/JS를 캐시해 두고 계속 쓰는 문제를 막아 줍니다.
    (파일을 수정하지 않은 경우에는 주소가 그대로라서 캐시가 정상적으로 활용됩니다.)
    """

    def url(self, name):
        url = super().url(name)
        try:
            path = finders.find(name)
            if path:
                version = int(os.path.getmtime(path))
                url += ('&' if '?' in url else '?') + 'v=%d' % version
        except Exception:
            # 버전 계산에 실패해도 사이트가 멈추지 않도록 원래 주소를 그대로 사용
            pass
        return url
