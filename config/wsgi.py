"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# 서버(SQLITE_DIR 환경변수가 있을 때)에서는 DB를 재배포해도 보존되는 폴더에 두기 때문에,
# 서버가 시작될 때 아직 적용되지 않은 마이그레이션(예: 플래너 테이블)을 자동으로 적용합니다.
if os.environ.get('SQLITE_DIR'):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False, verbosity=0)
    except Exception as exc:  # 마이그레이션 실패가 사이트 전체를 멈추지 않게 함
        print(f'[migrate 실패] {exc}')
