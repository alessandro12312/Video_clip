import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ===============================================
# CONFIGURAZIONE MINIO E MEDIA FILES
# ===============================================
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

USE_MINIO_STORAGE = True
DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = 'localhost:9000'
MINIO_STORAGE_ACCESS_KEY = 'console'
MINIO_STORAGE_SECRET_KEY = 'console_access_key'
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_OBJECT_METADATA = {"Cache-Control": "max-age=1000"}
MINIO_STORAGE_MEDIA_BUCKET_NAME = 'clips'
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = 'clips'
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = '%c/'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_STATIC_BUCKET_NAME = 'clips'
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True

# if USE_MINIO_STORAGE:
#     print("✅ Storage dei media file configurato su MinIO.")
    
    # # Imposta il backend di storage predefinito per i file media
    # DEFAULT_FILE_STORAGE = 'minio_storage.storage.MinioMediaStorage'

    # # Endpoint del server MinIO (localhost:9000)
    # MINIO_STORAGE_ENDPOINT = os.getenv("MINIO_ENDPOINT")

    # # Credenziali di accesso a MinIO
    # MINIO_STORAGE_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    # MINIO_STORAGE_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
    
    # # Nome del bucket su MinIO dove salvare i file
    # MINIO_STORAGE_MEDIA_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')

    # # Impostazioni di sicurezza e creazione bucket
    # MINIO_STORAGE_USE_HTTPS = os.getenv('MINIO_USE_HTTPS', 'False').lower() == 'true'
    # MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True  # Consigliato False: crea il bucket manualmente per maggior controllo


    # ***** AGGIUNGI QUESTI PRINT TEMPORANEI *****
    # print(f"DEBUG_MINIO: Endpoint = {MINIO_STORAGE_ENDPOINT}")
    # print(f"DEBUG_MINIO: Access Key = {MINIO_STORAGE_ACCESS_KEY}") # Non mostrare in log di produzione!
    # print(f"DEBUG_MINIO: Secret Key = {MINIO_STORAGE_SECRET_KEY}") # Non mostrare in log di produzione!
    # print(f"DEBUG_MINIO: Bucket Name = {MINIO_STORAGE_MEDIA_BUCKET_NAME}")
    # **********************************************


    # Per default, la libreria genera URL "pre-firmati" (privati e con scadenza).
    # Questa è l'opzione più sicura e non richiede di impostare MEDIA_URL.
    # Se vuoi invece che i file siano sempre accessibili pubblicamente, decommenta le righe seguenti:
    # MINIO_STORAGE_PUBLIC_URLS = True
    # protocol = "https" if MINIO_STORAGE_USE_HTTPS else "http"
    # MEDIA_URL = f"{protocol}://{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}/"

# else:
#     # Fallback: storage locale se MinIO non è configurato
#     print("⚠️  Storage dei media file configurato in locale.")
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = BASE_DIR / "media"

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
    'minio_storage',
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
    'PAGE_SIZE': 10,
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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # You might have other handlers like file handlers
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            'propagate': False,
        },
        'minio_storage': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print(f"DEBUG: DEFAULT_FILE_STORAGE = {DEFAULT_FILE_STORAGE}")
print("SETTINGS MODULE LOADING...")