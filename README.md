Enlace Software : https://django-gestion-eventos.onrender.com/

-----------------------

Descripción del Proyecto (EventSoft)


EventSoft es un aplicativo web basado en la gestión integral de eventos académicos, diseñado para facilitar la organización, administración y seguimiento de diferentes actividades relacionadas con congresos, seminarios, ferias, capacitaciones, talleres y demás eventos institucionales.

-Asistentes: Usuarios que se registran para participar en los eventos, visualizar las actividades, descargar certificados y realizar inscripciones.

-Expositores: Encargados de presentar ponencias o proyectos. Pueden subir archivos, actualizar información de su presentación y consultar la programación asignada.

-Evaluadores: Responsables de calificar las ponencias o trabajos presentados. Acceden a las presentaciones, asignan puntajes y generan retroalimentación.

-Administradores: Gestionan eventos, controlan la base de participantes, asignan evaluadores, configuran la programación y administran la plataforma a nivel operativo.

-Super Administradores: Tienen control total sobre el sistema. Pueden crear administradores, configurar módulos avanzados, gestionar permisos y supervisar todas las operaciones del evento.

Como resultado, se obtuvo una aplicación que cumple con los requerimientos planteados, mejora los tiempos de respuesta en un 100% efectiva y facilita la interacción entre usuarios y procesos. Las pruebas realizadas evidenciaron que el software es confiable, escalable y de fácil adopción.

En conclusión, el proyecto contribuye a la modernización del campo de aplicación y demuestra la pertinencia de integrar metodologías ágiles en el desarrollo de soluciones tecnológicas con impacto real en el entorno organizacional.

--------------------------

INTEGRANTES DEL EQUIPO 

Juan José Orrego Urrea
Juan Esteban Marulanda Lopez
Juan Manuel Tayak


---------------------------

PASOS PARA EJECUTAR EL PROYECTO EN LINEA

CONFIGURA LA MEDIA CON (CLAUDINARY)

PASO 1: Crear una cuenta en Cloudinary
- Ir a Cloudinary
- Crear cuenta

PASO 2: Crear un Cloud (automático)
- Cloudinary crea automáticamente el Cloud al registrarse

PASO 3: Obtener credenciales
- Ingresar al Dashboard
- Copiar:
  CLOUD NAME
  API KEY
  API SECRET

PASO 4: Configurar acceso público (automático)
- Cloudinary permite acceso público por defecto
- No se configuran políticas ni permisos


PASO 5: Instalar dependencias (si no existen)
cloudinary
django-cloudinary-storage


PASO 6: Verificar configuración en settings.py
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


PASO 7: Copiar y pegar en el entorno (Render / Producción)
CLOUDINARY_CLOUD_NAME=****************
CLOUDINARY_API_KEY=****************
CLOUDINARY_API_SECRET=****************


PASO 8: Desplegar el proyecto
- Subir archivos desde el sistema
- Los archivos media se almacenan automáticamente en Cloudinary

CONFIGURA LOS CORREOS CON (BREVO)

PASO 1: Crear una cuenta en Brevo

PASO 2: Ir a Configuración → SMTP Y API

PASO 3: Generar una Clave API

PASO 4: Copiar y pegar en el entorno de Render:

USE_BREVO=True
BREVO_API_KEY=******************************************
DEFAULT_FROM_EMAIL=Event-Soft <tucorreoaqui@gmail.com>
⚠️ NOTA IMPORTANTE: Debes tener un correo verificado en Brevo, el cual será el DEFAULT_FROM_EMAIL




------------------------------


¿Cómo clonar EventSoft?


1) Clonar el repositorio con el siguiente enlace https://github.com/Juanes2006/DJANGO---GESTION_EVENTOS-.git
2) Ubicate en la carpeta:
   cd DJANGO---GESTIÓN_EVENTOS-
   
3) Instala el entorno virtual con el siguiente comando:
   python -m venv venv
   
4) Debes activar el entorno virtual:
   venv\Scripts\activate
   
7) Instala todas las dependencias con el siguiente comando:
   pip install -r requirements.txt

8) Sube las migraciones:
   python manage.py migrate
   
9) Crea un superusuario con el siguiente comando:
    python manage.py createsuperuser

10) Crear un archivo .env en la raíz del proyecto con el siguiente contenido:
    # ----- DJANGO -----
SECRET_KEY=tu_clave_secreta_super_segura
DEBUG=True

# ----- BASE DE DATOS LOCAL -----
DB_NAME=nombre_de_la_base_de_datos
DB_USER=root
DB_PASSWORD=****
DB_HOST=localhost
DB_PORT=3306

# ----- CORREO GMAIL LOCAL -----
EMAIL_HOST_USER=tucorreoaqui@gmail.com
EMAIL_HOST_PASSWORD=**** **** **** ****
DEFAULT_FROM_EMAIL=Event-Soft <tucorreoaqui@gmail.com>

# ----- EMAIL (BREVO) -----
USE_BREVO=False
BREVO_API_KEY=******************************************
DEFAULT_FROM_EMAIL=Event-Soft <tucorreoaqui@gmail.com>

# ----- AWS S3 (solo necesario en producción) -----
AWS_ACCESS_KEY_ID=****************
AWS_SECRET_ACCESS_KEY=***********************************
AWS_STORAGE_BUCKET_NAME=Nombre-Bucket-AWS-S3
AWS_S3_REGION_NAME=us-east-#

# ----- CORREO SUPERUSER -----
SUPERADMIN_EMAIL=correosuperadmin@gmail.com

11) Y ya por ultimo corre el servidor para que disfrutes de EventSoft

