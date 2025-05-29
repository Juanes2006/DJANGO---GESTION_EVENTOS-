import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def save_file(file, upload_folder_key='pagos'):
    """
    Guarda un archivo en la carpeta especificada dentro de settings.

    Parámetros:
    - file: objeto UploadedFile
    - upload_folder_key: clave para identificar carpeta y extensiones permitidas ('imagenes', 'pagos', 'programacion')

    Retorna:
    - nombre del archivo guardado (string) o None si no es válido
    """

    # Obtener carpeta y extensiones permitidas desde settings
    upload_folder = settings.UPLOAD_SETTINGS['FOLDERS'].get(upload_folder_key)
    allowed_extensions = settings.UPLOAD_SETTINGS['ALLOWED_EXTENSIONS'].get(upload_folder_key, set())

    if not upload_folder or not allowed_extensions:
        return None

    # Validar extensión
    filename = file.name
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_extensions:
        return None

    # Guardar archivo usando FileSystemStorage
    fs = FileSystemStorage(location=upload_folder)
    saved_filename = fs.save(filename, file)
    return saved_filename
