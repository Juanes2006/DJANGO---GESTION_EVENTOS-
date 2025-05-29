from django.db import models
from app_admin.models import AdministradorEvento
from app_super_admin.models import Categoria

class Evento(models.Model):
    eve_id = models.AutoField(primary_key=True)
    eve_nombre = models.CharField(max_length=100)
    eve_descripcion = models.CharField(max_length=400, null=True, blank=True)
    eve_ciudad = models.CharField(max_length=45, null=True, blank=True)
    eve_lugar = models.CharField(max_length=45, null=True, blank=True)
    eve_fecha_inicio = models.DateField(null=True, blank=True)
    eve_fecha_fin = models.DateField(null=True, blank=True)
    eve_estado = models.CharField(max_length=45, null=True, blank=True)
    adm_id = models.ForeignKey(AdministradorEvento, on_delete=models.CASCADE, related_name='eventos')
    cobro = models.CharField(max_length=2, default="No")
    cupos = models.IntegerField(null=True, blank=True)
    imagen = models.CharField(max_length=255, null=True, blank=True)
    archivo_programacion = models.CharField(max_length=255, null=True, blank=True)
    inscripciones_participantes_abiertas = models.BooleanField(default=True)
    inscripciones_asistentes_abiertas = models.BooleanField(default=True)
    categorias = models.ManyToManyField(Categoria, through='EventoCategoria', related_name='eventos')


    def get_participant_count(self):
        return self.participantes.count()

class EventoCategoria(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('evento', 'categoria')
