from django.db import models
from app_usuarios.models import Usuario
from app_eventos.models import Evento
from cloudinary.models import CloudinaryField

class Asistentes(models.Model):
    
    ########### NUEVO CAMPO PARA RELACIONAR CON USUARIO ###########
    usuario = models.OneToOneField(Usuario,null=True, on_delete=models.CASCADE)

    def _str_(self):
        return f"Asistente: {self.usuario.username}"


   

class AsistentesEventos(models.Model):
    asi_eve_asistente_fk = models.ForeignKey(Asistentes, null=True, on_delete=models.CASCADE)
    asi_eve_evento_fk = models.ForeignKey(Evento, null=True, on_delete=models.CASCADE)
    asi_eve_fecha_hora = models.DateTimeField()
# soporte Cloudinary: imágenes, PDFs, documentos o videos
    asi_eve_soporte = CloudinaryField(
        resource_type="auto",   # permite cualquier tipo de archivo: image, pdf, doc, video, audio
        folder="soportes_eventos/",   # carpeta dentro de Cloudinary
        null=True,
        blank=True
    )    
    asi_eve_estado = models.CharField(max_length=45)
    asi_eve_clave = models.CharField(max_length=45)

    class Meta:
        unique_together = ('asi_eve_asistente_fk', 'asi_eve_evento_fk')
