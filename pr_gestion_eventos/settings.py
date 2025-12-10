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
load_dotenv(dotenv_path=BASE_DIR / '.env')

# ==========================
# SECURITY
# ==========================
SECRET_KEY = os.environ.get("SECRET_KEY") or get_random_secret_key()
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
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',

    # Terceros

    # Tus apps
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
            os.path.join(BASE_DIR, 'templates'),
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
# DATABASE
# ==========================
# BASE DE DATOS MYSQL LOCAL CONFIGURACIÓN



DATABASES = {
   'default': dj_database_url.config(conn_max_age=600, ssl_require=not DEBUG)
}

#Conexion base de datos local MYSQL workbech

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
##        'NAME': 'eventos',
#        'USER': 'root',
#        'PASSWORD': 'root',
#        'HOST': 'localhost',
#        'PORT': '3306',
#    }
#}


# ==========================
# AUTH PASSWORD VALIDATION
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
# STATIC FILES
# ==========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ==========================
# MEDIA FILES
# ==========================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================
# UPLOADS LOCALES
# ==========================
UPLOAD_FOLDER_IMAGENES = os.path.join(BASE_DIR, 'static', 'imagenes')
UPLOAD_FOLDER_PAGOS = os.path.join(BASE_DIR, 'static', 'uploads')
UPLOAD_FOLDER_PROGRAMACION = os.path.join(BASE_DIR, 'static', 'programacion')

ALLOWED_EXTENSIONS_IMAGENES = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
ALLOWED_EXTENSIONS_PAGOS = {'png', 'jpg', 'jpeg', 'pdf'}
ALLOWED_EXTENSIONS_PROGRAMACION = {'pdf'}

MAX_FILE_SIZE_IMAGENES = 5 * 1024 * 1024
MAX_FILE_SIZE_PAGOS = 10 * 1024 * 1024
MAX_FILE_SIZE_PROGRAMACION = 50 * 1024 * 1024

UPLOAD_SETTINGS = {
    'FOLDERS': {
        'imagenes': UPLOAD_FOLDER_IMAGENES,
        'pagos': UPLOAD_FOLDER_PAGOS,
        'programacion': UPLOAD_FOLDER_PROGRAMACION,
    },
    'ALLOWED_EXTENSIONS': {
        'imagenes': ALLOWED_EXTENSIONS_IMAGENES,
        'pagos': ALLOWED_EXTENSIONS_PAGOS,
        'programacion': ALLOWED_EXTENSIONS_PROGRAMACION,
    },
    'MAX_SIZES': {
        'imagenes': MAX_FILE_SIZE_IMAGENES,
        'pagos': MAX_FILE_SIZE_PAGOS,
        'programacion': MAX_FILE_SIZE_PROGRAMACION,
    }
}

def create_upload_folders():
    for folder in UPLOAD_SETTINGS['FOLDERS'].values():
        os.makedirs(folder, exist_ok=True)

create_upload_folders()

def is_allowed_file(filename, file_type='imagenes'):
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in UPLOAD_SETTINGS['ALLOWED_EXTENSIONS'].get(file_type, set())

# ==========================
# LOGIN URL
# ==========================
LOGIN_URL = 'main:login'

# ==========================
# EMAIL (Brevo o Gmail)
# ==========================
USE_BREVO = config("USE_BREVO", default=False, cast=bool)
if USE_BREVO:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER")
    ANYMAIL = {"BREVO_API_KEY": config("BREVO_API_KEY")}
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST_LOCAL')
    EMAIL_PORT = config('EMAIL_PORT_LOCAL', cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS_LOCAL', cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER_LOCAL')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD_LOCAL')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==========================
# claudinary settings
# ==========================
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

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
import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'DEBUG'},
}

# ==========================
# QR Settings
# ==========================
QR_SETTINGS = {
    'DEFAULT_SIZE': 10,
    'DEFAULT_BORDER': 4,
    'FORMAT': 'PNG',
    'FILL_COLOR': 'black',
    'BACK_COLOR': 'white',
}

# ==========================
# Otros Settings de apps
# ==========================
EVENTOS_SETTINGS = {'MAX_PARTICIPANTES_DEFAULT': 100, 'DIAS_LIMITE_INSCRIPCION': 7, 'FORMATO_FECHA': '%d/%m/%Y'}
REGISTROS_SETTINGS = {'GENERAR_OR_AUTOMATICO': True, 'PREFIJO_OR': 'OR-', 'LONGITUD_OR': 8}
NOTIFICATIONS_SETTINGS = {'SEND_EMAIL_CONFIRMATION': True, 'ADMIN_EMAIL': 'admin@tueventos.com', 'FROM_EMAIL': 'noreply@tueventos.com'}
