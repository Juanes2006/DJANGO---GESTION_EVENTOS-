from django.db import models
from app_eventos.models import Evento

class Participantes(models.Model):
    par_id = models.CharField(primary_key=True, max_length=20)
    par_nombre = models.CharField(max_length=100)
    par_correo = models.CharField(max_length=100)
    par_telefono = models.CharField(max_length=45)

    def __str__(self):
        return self.par_nombre

class ParticipantesEventos(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
    )

    par_eve_participante_fk = models.ForeignKey(Participantes, on_delete=models.CASCADE)
    par_eve_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE)
    par_eve_fecha_hora = models.DateTimeField()
    par_eve_documentos = models.CharField(max_length=255, null=True, blank=True)
    par_eve_or = models.CharField(max_length=255, null=True, blank=True)
    par_eve_clave = models.CharField(max_length=45)
    par_estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

    class Meta:
        unique_together = ('par_eve_participante_fk', 'par_eve_evento_fk')
