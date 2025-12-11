from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
import dj_database_url
from decouple import config
from dotenv import load_dotenv

# ==========================
# BASE DIR Y ENV VARIABLES
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ⛔ SOLO DESARROLLO
# En producción (Render) no hace falta cargar .env manualmente
# load_dotenv(dotenv_path=BASE_DIR / '.env')

# ==========================
# SECURITY
# ==========================
SECRET_KEY = os.environ.get("SECRET_KEY") or get_random_secret_key()

# ⛔ DEBUG debe ser FALSE en producción (Render define la variable)
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
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

    'cloudinary',
    'cloudinary_storage',

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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ NECESARIO EN PRODUCCIÓN
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pr_gestion_eventos.urls'

# ==========================
# TEMPLATES ✅ OBLIGATORIO (ADMIN)
# ==========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # ⛔ RUTAS EXTRA NO NECESARIAS EN PRODUCCIÓN
        # Django ya carga templates desde las apps automáticamente
        # 'DIRS': [
        #     os.path.join(BASE_DIR, 'templates'),
        #     'app_admin/templates',
        #     'app_evaluadores/templates',
        #     'app_eventos/templates',
        #     'app_main/templates',
        #     'app_participantes/templates',
        #     'app_qr/templates',
        #     'app_registros/templates',
        #     'app_super_admin/templates',
        #     'app_asistentes/templates',
        # ],

        'DIRS': [BASE_DIR / 'templates'],  # ✅ RECOMENDADO
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
# DATABASE ✅ PRODUCCIÓN
# ==========================
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# ⛔ SOLO DESARROLLO LOCAL (MYSQL WORKBENCH)
#DATABASES = {
#     'default': {
##         'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'eventos',
#         'USER': 'root',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
#     }

# ==========================
# AUTH PASSWORD VALIDATION ✅
# ==========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================
# INTERNATIONALIZATION ✅
# ==========================
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ==========================
# STATIC FILES ✅
# ==========================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ⛔ LOCAL ONLY
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# ==========================
# MEDIA FILES ⛔ NO USADAS (CLOUDINARY)
# ==========================
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# ==========================
# UPLOADS LOCALES ⛔ NO USAR EN PRODUCCIÓN
# (Cloudinary ya gestiona todo)
# ==========================
# UPLOAD_FOLDER_IMAGENES = os.path.join(BASE_DIR, 'static', 'imagenes')
# UPLOAD_FOLDER_PAGOS = os.path.join(BASE_DIR, 'static', 'uploads')
# UPLOAD_FOLDER_PROGRAMACION = os.path.join(BASE_DIR, 'static', 'programacion')

# ALLOWED_EXTENSIONS_IMAGENES = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
# ALLOWED_EXTENSIONS_PAGOS = {'png', 'jpg', 'jpeg', 'pdf'}
# ALLOWED_EXTENSIONS_PROGRAMACION = {'pdf'}

# MAX_FILE_SIZE_IMAGENES = 5 * 1024 * 1024
# MAX_FILE_SIZE_PAGOS = 10 * 1024 * 1024
# MAX_FILE_SIZE_PROGRAMACION = 50 * 1024 * 1024

# ⛔ FUNCIONES DE SISTEMA DE ARCHIVOS LOCAL
# def create_upload_folders():
#     pass
#
# def is_allowed_file(filename, file_type='imagenes'):
#     pass

# ==========================
# LOGIN ✅
# ==========================
LOGIN_URL = 'main:login'

# ==========================
# EMAIL ✅ (BREVO PRODUCCIÓN)
# ==========================
USE_BREVO = config("USE_BREVO", default=False, cast=bool)

if USE_BREVO:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER")
    ANYMAIL = {"BREVO_API_KEY": config("BREVO_API_KEY")}
else:
    # ⛔ SOLO DESARROLLO LOCAL
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_HOST = config('EMAIL_HOST_LOCAL')
    # EMAIL_PORT = config('EMAIL_PORT_LOCAL', cast=int)
    # EMAIL_USE_TLS = config('EMAIL_USE_TLS_LOCAL', cast=bool)
    # EMAIL_HOST_USER = config('EMAIL_HOST_USER_LOCAL')
    # EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD_LOCAL')

# ==========================
# CLOUDINARY ✅ PRODUCCIÓN
# ==========================
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv("CLOUDINARY_CLOUD_NAME"),
    'API_KEY': os.getenv("CLOUDINARY_API_KEY"),
    'API_SECRET': os.getenv("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ==========================
# SEGURIDAD ✅
# ==========================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ==========================
# LOGGING ⛔ DEBUG EXCESIVO EN PRODUCCIÓN
# ==========================
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
#     },
#     'root': {'handlers': ['console'], 'level': 'DEBUG'},
# }

# ==========================
# QR SETTINGS ✅ (NO PROBLEMA)
# ==========================
QR_SETTINGS = {
    'DEFAULT_SIZE': 10,
    'DEFAULT_BORDER': 4,
    'FORMAT': 'PNG',
    'FILL_COLOR': 'black',
    'BACK_COLOR': 'white',
}

# ==========================
# OTROS SETTINGS ✅
# ==========================
EVENTOS_SETTINGS = {'MAX_PARTICIPANTES_DEFAULT': 100, 'DIAS_LIMITE_INSCRIPCION': 7, 'FORMATO_FECHA': '%d/%m/%Y'}
REGISTROS_SETTINGS = {'GENERAR_OR_AUTOMATICO': True, 'PREFIJO_OR': 'OR-', 'LONGITUD_OR': 8}
NOTIFICATIONS_SETTINGS = {'SEND_EMAIL_CONFIRMATION': True}
