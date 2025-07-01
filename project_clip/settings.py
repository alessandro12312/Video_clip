import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Define the root directory for logs
LOGS_ROOT = BASE_DIR / "logs"

# Security settings
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key-here")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1").split()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'minio_storage',  # Aggiunto per django-storages (MinIO)
    'cs_clips',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_clip.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'project_clip.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': '127.0.0.1',  # Cambiato da postgres_db a 127.0.0.1
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}


# ===============================================
# CONFIGURAZIONE MINIO S3 STORAGE
# ===============================================

# Usa MinIO solo se le variabili d'ambiente sono configurate
USE_S3_STORAGE = bool(os.getenv('AWS_S3_URL'))

if USE_S3_STORAGE:
    # Configurazione per django-storages con MinIO
    #DEFAULT_FILE_STORAGE = 'cs_clips.storage_backends.S3MediaStorage'
    DEFAULT_FILE_STORAGE = 'minio_storage.storage.MinioMediaStorage'

    # Credenziali MinIO (compatibili con AWS S3)
    MINIO_STORAGE_SECRET_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    MINIO_STORAGE_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    MINIO_STORAGE_MEDIA_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    MINIO_STORAGE_ENDPOINT = os.getenv("AWS_S3_URL")
    #MINIO_ACCESS_URL = os.getenv("MINIO_ACCESS_URL")
    MINIO_STORAGE_USE_HTTPS = False
    MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = False

    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-west-1')
    
    # Configurazioni SSL per MinIO locale
    AWS_S3_USE_SSL = os.getenv('AWS_S3_USE_SSL', 'False').lower() == 'true'
    AWS_S3_VERIFY = os.getenv('AWS_S3_VERIFY', 'False').lower() == 'true'
    
    # Configurazioni file storage
    AWS_S3_FILE_OVERWRITE = os.getenv('AWS_S3_FILE_OVERWRITE', 'False').lower() == 'true'
    AWS_DEFAULT_ACL = None  # Nessun ACL di default
    AWS_QUERYSTRING_AUTH = os.getenv('AWS_QUERYSTRING_AUTH', 'False').lower() == 'true'
    

    # Override MEDIA_URL per usare MinIO
    #MEDIA_URL = f'{MINIO_STORAGE_ENDPOINT}/'
    
    print(f"✅ MinIO Storage configurato - Endpoint: {MINIO_STORAGE_ENDPOINT}")
    print(f"✅ Bucket: {MINIO_STORAGE_ENDPOINT}")
    
else:
    # Fallback: storage locale se MinIO non è configurato
    print("⚠️  MinIO non configurato, usando storage locale")

# ===============================================


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name} - {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file.errors': {
            'class': 'logging.FileHandler',
            'filename': LOGS_ROOT / 'handler' / 'errors.log',
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },

    'loggers': {
        'cs_clips.errors': {
            'handlers': ['console', 'file.errors'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'cs_clips.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2, # Default page size for pagination for testing
}

# JWT Authentication settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ===============================================
# STATIC & MEDIA FILES CONFIGURATION
# ===============================================

STATIC_URL = "/static/"
STATICFILES_LOCATION = "static"
STATICFILES_STORAGE = "blogs.storage.StaticS3Boto3Storage"

# Media files: configurazione condizionale basata su MinIO
if not USE_S3_STORAGE:
    print('DEBUG USE_S3_STORAGE null AWS_S3_URL:', os.getenv('AWS_S3_URL'))
    # Storage locale (fallback)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"
else:
    print('DEBUG USE_S3_STORAGE not null AWS_S3_URL:', os.getenv('AWS_S3_URL'))
    print('DEBUG USE_S3_STORAGE not null DEFAULT_FILE_STORAGE:', DEFAULT_FILE_STORAGE)
    print('DEBUG USE_S3_STORAGE not null MEDIA_URL:', MINIO_STORAGE_ENDPOINT)
# Se USE_S3_STORAGE è True, MEDIA_URL è già configurato sopra nella sezione MinIO

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===============================================


# ===============================================
# CONFIGURAZIONI UPLOAD FILE
# ===============================================

# Dimensione massima file upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
# DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB

# Formati video consentiti
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
# MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB