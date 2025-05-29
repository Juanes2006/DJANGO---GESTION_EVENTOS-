from django.db import models
from app_eventos.models import Evento

class Asistentes(models.Model):
    asi_id = models.CharField(primary_key=True, max_length=20)
    asi_nombre = models.CharField(max_length=100)
    asi_correo = models.CharField(max_length=100)
    asi_telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.asi_nombre

class AsistentesEventos(models.Model):
    asi_eve_asistente_fk = models.ForeignKey(Asistentes, on_delete=models.CASCADE)
    asi_eve_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE)
    asi_eve_fecha_hora = models.DateTimeField()
    asi_eve_soporte = models.CharField(max_length=255, null=True, blank=True)
    asi_eve_estado = models.CharField(max_length=45)
    asi_eve_clave = models.CharField(max_length=45)

    class Meta:
        unique_together = ('asi_eve_asistente_fk', 'asi_eve_evento_fk')
