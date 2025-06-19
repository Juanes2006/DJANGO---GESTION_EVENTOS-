from django.db import models
from app_eventos.models import Evento
from app_usuarios.models import Usuario

class Participantes(models.Model):
    
    
    #### NUEVO CAMPO PARA RELACIONAR CON USUARIO ####
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def _str_(self):
        return f"Participante: {self.usuario.username}"


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
