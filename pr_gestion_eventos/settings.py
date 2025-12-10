from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
import dj_database_url
from decouple import config
from dotenv import load_dotenv

# ==========================
# BASE DIR
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

# ==========================
# SECURITY
# ==========================
SECRET_KEY = os.environ.get("SECRET_KEY") or get_random_secret_key()

# ✅ PRODUCCIÓN → DEBUG SIEMPRE FALSE
DEBUG = False

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

SITE_ID = 1

# ==========================
# APPLICATIONS
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ✅ Cloudinary (Producción)
    'cloudinary',
    'cloudinary_storage',

    # Apps
    'app_usuarios',
    'app_admin',
    'app_evaluadores',
    'app_asistentes',
    'app_eventos',
    'app_main',
    'app_participantes',
    'app_qr',
    'app_registros',
    'app_super_admin',
]

AUTH_USER_MODEL = 'app_usuarios.Usuario'

# ==========================
# MIDDLEWARE
# ==========================
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

ROOT_URLCONF = 'pr_gestion_eventos.urls'

# ==========================
# TEMPLATES
# ==========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            'app_admin/templates',
            'app_evaluadores/templates',
            'app_eventos/templates',
            'app_main/templates',
            'app_participantes/templates',
            'app_qr/templates',
            'app_registros/templates',
            'app_super_admin/templates',
            'app_asistentes/templates',
        ],
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

WSGI_APPLICATION = 'pr_gestion_eventos.wsgi.application'

# ==========================
# DATABASE (Render / Postgres)
# ==========================
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
}

# ❌ MYSQL LOCAL (NO PRODUCCIÓN)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'eventos',
#         'USER': 'root',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

# ==========================
# PASSWORD VALIDATION
# ==========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================
# INTERNATIONALIZATION
# ==========================
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ==========================
# STATIC FILES (Producción)
# ==========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ❌ SOLO DESARROLLO
# STATICFILES_DIRS = [BASE_DIR / 'static']

# ==========================
# MEDIA FILES
# ❌ NO USAR EN CLOUNDINARY / PRODUCCIÓN
# ==========================
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# ==========================
# CLOUDINARY (UPLOADS REALES)
# ==========================
import cloudinary

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ==========================
# LOGIN
# ==========================
LOGIN_URL = 'main:login'

# ==========================
# EMAIL
# ==========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST_LOCAL')
EMAIL_PORT = config('EMAIL_PORT_LOCAL', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS_LOCAL', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER_LOCAL')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD_LOCAL')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==========================
# SECURITY HEADERS
# ==========================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ==========================
# LOGGING (PRODUCCIÓN)
# ==========================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',  # ✅ NO DEBUG EN PRODUCCIÓN
    },
}

# ==========================
# APP SETTINGS
# ==========================
EVENTOS_SETTINGS = {
    'MAX_PARTICIPANTES_DEFAULT': 100,
    'DIAS_LIMITE_INSCRIPCION': 7,
    'FORMATO_FECHA': '%d/%m/%Y'
}
