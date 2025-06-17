import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def save_file(file, upload_folder=None, allowed_extensions=None):
    if not upload_folder or not allowed_extensions:
        return None

    # Validar extensión
    filename = file.name
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_extensions:
        return None

    fs = FileSystemStorage(location=upload_folder)
    saved_filename = fs.save(filename, file)
    return saved_filename
