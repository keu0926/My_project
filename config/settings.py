from pathlib import Path
import os
import shutil

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-th5044537pribs)!0#(w@iykp&yfk87qk$j0q$o97!&ew_1@!j'

DEBUG = True

ALLOWED_HOSTS = ['.mycafe24.ai', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = ['https://*.mycafe24.ai']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'planner',  # ★ 학습 플래너 전용 앱
    'total_schedule',
    'academy_admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# 서버(카페24 AI 스페이스)에서는 재배포해도 보존되는 폴더(/app/user_data)에 DB 파일을 둡니다.
# 서버에 SQLITE_DIR 환경변수가 설정되어 있으며, 내 컴퓨터(환경변수 없음)에서는 기존처럼 프로젝트 폴더의 db.sqlite3 를 씁니다.
_sqlite_dir = os.environ.get('SQLITE_DIR')
if _sqlite_dir:
    _sqlite_dir = Path(_sqlite_dir)
    _sqlite_dir.mkdir(parents=True, exist_ok=True)
    DB_FILE = _sqlite_dir / 'db.sqlite3'

    # 서버에 DB 파일이 아직 없을 때만(최초 1회) 저장소의 db.sqlite3(기존 회원·공지 등)를 복사해 시작합니다.
    _seed = BASE_DIR / 'db.sqlite3'
    if not DB_FILE.exists() and _seed.exists():
        _tmp = DB_FILE.with_name(DB_FILE.name + '.seeding')
        shutil.copy2(_seed, _tmp)
        os.replace(_tmp, DB_FILE)
else:
    DB_FILE = BASE_DIR / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_FILE,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

# 플래너의 '오늘' 날짜와 화면에 보이는 시각이 한국 시간 기준이 되도록 설정 (DB에는 UTC로 저장됨)
TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# {% static %} 주소 끝에 ?v=<수정시간> 을 붙여 인앱 브라우저의 예전 캐시를 무력화
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'config.storage.VersionedStaticFilesStorage',
    },
}

# Email Configuration (Django 표준 설정 방식)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kangromin@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = "kangromin@gmail.com"
ADMIN_CONSULT_EMAIL = "puppytk@naver.com"
