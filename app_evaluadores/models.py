from django.db import models
from app_eventos.models import Evento
from app_participantes.models import Participantes

class Evaluador(models.Model):
    eva_id = models.CharField(primary_key=True, max_length=20)
    eva_nombre = models.CharField(max_length=100)
    eva_correo = models.CharField(max_length=100)
    eva_telefono = models.CharField(max_length=45)
    eventos = models.ManyToManyField(Evento, through='EvaluadorEventos', related_name='evaluadores')


    def __str__(self):
        return self.eva_nombre
    

    
class EvaluadorEventos(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
    )
    
    eva_eve_evaluador_fk = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    eva_eve_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE)
    eva_eve_fecha_hora = models.DateTimeField()
    eva_eve_documentos = models.CharField(max_length=255, null=True, blank=True)
    eva_eve_or = models.CharField(max_length=255, null=True, blank=True)
    eva_eve_clave = models.CharField(max_length=45)
    eva_estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')
    
    class Meta:
        unique_together = ('eva_eve_evaluador_fk', 'eva_eve_evento_fk')
    
    def __str__(self):
        return f"{self.eva_eve_evaluador_fk.eva_nombre} - {self.eva_eve_evento_fk} - {self.eva_estado}"


class Criterio(models.Model):
    cri_id = models.AutoField(primary_key=True) 
    cri_descripcion = models.CharField(max_length=100)
    cri_peso = models.FloatField()
    cri_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE)  # ← CORRECTO

    def __str__(self):
        return self.cri_descripcion

class Calificacion(models.Model):
    id = models.AutoField(primary_key=True)
    cal_evaluador_fk = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    cal_criterio_fk = models.ForeignKey(Criterio, on_delete=models.CASCADE)
    cal_participante_fk = models.ForeignKey(Participantes, on_delete=models.CASCADE)
    cal_valor = models.IntegerField()

class Instrumento(models.Model):
    inst_id = models.AutoField(primary_key=True)
    inst_tipo = models.CharField(max_length=50)
    inst_descripcion = models.TextField()
    inst_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE)
    def __str__(self):
        return self.inst_tipo


class InformacionTecnica(models.Model):
    inf_id = models.AutoField(primary_key=True)
    inf_nombre = models.CharField(max_length=100)
    inf_descripcion = models.TextField()
    inf_evento_fk = models.ForeignKey(Evento, on_delete=models.CASCADE)
    def __str__(self):
        return self.inf_nombre