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

# ❌ NO USAR en producción (Render ya inyecta variables de entorno)
# load_dotenv(dotenv_path=BASE_DIR / '.env')

# ==========================
# SECURITY
# ==========================

# ⚠️ En producción el SECRET_KEY DEBE venir del entorno SIEMPRE
# esta línea puede generar claves nuevas si falla el env
SECRET_KEY = os.environ.get("SECRET_KEY") or get_random_secret_key()

# ✅ Correcto para producción
DEBUG = 'RENDER' not in os.environ

# ⚠️ ALLOWED_HOSTS vacío puede causar errores si falla RENDER_EXTERNAL_HOSTNAME
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

    # ✅ Necesario en producción
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
# DATABASE
# ==========================

# ✅ PRODUCCIÓN (DATABASE_URL)
DATABASES = {
   'default': dj_database_url.config(conn_max_age=600, ssl_require=not DEBUG)
}

# ❌ SOLO DESARROLLO LOCAL — causa errores si se activa en producción
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'eventos',
#        'USER': 'root',
#        'PASSWORD': 'root',
#        'HOST': 'localhost',
#        'PORT': '3306',
#    }
#}

# ==========================
# STATIC FILES
# ==========================

STATIC_URL = '/static/'

# ❌ NO necesario en producción, puede romper collectstatic
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# ✅ requerido en producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ==========================
# MEDIA FILES
# ==========================

# ❌ NO SE USA en producción con Cloudinary
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# ==========================
# UPLOADS LOCALES
# ==========================

# ❌ Cloudinary maneja media en producción
# estas rutas locales pueden causar errores en Render

# UPLOAD_FOLDER_IMAGENES = os.path.join(BASE_DIR, 'static', 'imagenes')
# UPLOAD_FOLDER_PAGOS = os.path.join(BASE_DIR, 'static', 'uploads')
# UPLOAD_FOLDER_PROGRAMACION = os.path.join(BASE_DIR, 'static', 'programacion')

# ✅ Estas validaciones son lógicas (NO causan error)
ALLOWED_EXTENSIONS_IMAGENES = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
ALLOWED_EXTENSIONS_PAGOS = {'png', 'jpg', 'jpeg', 'pdf'}
ALLOWED_EXTENSIONS_PROGRAMACION = {'pdf'}

MAX_FILE_SIZE_IMAGENES = 5 * 1024 * 1024
MAX_FILE_SIZE_PAGOS = 10 * 1024 * 1024
MAX_FILE_SIZE_PROGRAMACION = 50 * 1024 * 1024

# ❌ UPLOAD_SETTINGS con carpetas locales no sirve en producción
# UPLOAD_SETTINGS = { ... }

# ❌ NO crear carpetas en producción
# def create_upload_folders():
#     for folder in UPLOAD_SETTINGS['FOLDERS'].values():
#         os.makedirs(folder, exist_ok=True)
#
# create_upload_folders()

# ==========================
# LOGIN
# ==========================
LOGIN_URL = 'main:login'

# ==========================
# EMAIL
# ==========================

USE_BREVO = config("USE_BREVO", default=False, cast=bool)

if USE_BREVO:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER")
    ANYMAIL = {
        "BREVO_API_KEY": config("BREVO_API_KEY")
    }
else:
    # ⚠️ SOLO DESARROLLO LOCAL
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST_LOCAL', default='')
    EMAIL_PORT = config('EMAIL_PORT_LOCAL', cast=int, default=587)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS_LOCAL', cast=bool, default=True)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER_LOCAL', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD_LOCAL', default='')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ==========================
# CLOUDINARY
# ==========================

# ✅ CORRECTO para producción
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ==========================
# SEGURIDAD
# ==========================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ==========================
# LOGGING
# ==========================

# ❌ DEBUG logging en producción genera ruido y posibles leaks
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
#     },
#     'root': {'handlers': ['console'], 'level': 'DEBUG'},
# }

# ==========================
# SETTINGS DE APPS (SEGUROS)
# ==========================
QR_SETTINGS = {
    'DEFAULT_SIZE': 10,
    'DEFAULT_BORDER': 4,
    'FORMAT': 'PNG',
    'FILL_COLOR': 'black',
    'BACK_COLOR': 'white',
}

EVENTOS_SETTINGS = {'MAX_PARTICIPANTES_DEFAULT': 100}
REGISTROS_SETTINGS = {'GENERAR_OR_AUTOMATICO': True}
NOTIFICATIONS_SETTINGS = {'SEND_EMAIL_CONFIRMATION': True}
