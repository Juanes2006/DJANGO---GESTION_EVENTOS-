from django.db import models
from app_admin.models import AdministradorEvento
from app_super_admin.models import Categoria
from cloudinary.models import CloudinaryField
import uuid


class Evento(models.Model):
    eve_id = models.AutoField(primary_key=True)
    eve_nombre = models.CharField(max_length=100)
    eve_descripcion = models.CharField(max_length=400, null=True, blank=True)
    eve_ciudad = models.CharField(max_length=45, null=True, blank=True)
    eve_lugar = models.CharField(max_length=45, null=True, blank=True)
    eve_fecha_inicio = models.DateField(null=True, blank=True)
    eve_fecha_fin = models.DateField(null=True, blank=True)
    eve_estado = models.CharField(max_length=45, null=True, blank=True)

    adm_id = models.ForeignKey(
        AdministradorEvento,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    cobro = models.CharField(max_length=2, default="No")
    cupos = models.IntegerField(null=True, blank=True)

    # ✅ Imagen en Cloudinary
    imagen = CloudinaryField(
        'imagen',
        folder='eventos/imagenes',
        blank=True,
        null=True
    )

    # ✅ Archivo PDF / programa
    archivo_programacion = CloudinaryField(
        'archivo_programacion',
        resource_type='raw',
        folder='eventos/programacion',
        blank=True,
        null=True
    )

    inscripciones_participantes_abiertas = models.BooleanField(default=True)
    inscripciones_asistentes_abiertas = models.BooleanField(default=True)
    inscripciones_evaluadores_abiertas = models.BooleanField(default=True)

    categorias = models.ManyToManyField(
        Categoria,
        through='EventoCategoria',
        related_name='eventos'
    )

    def get_participant_count(self):
        return self.participantes.count() if hasattr(self, 'participantes') else 0

    def __str__(self):
        return self.eve_nombre


class EventoCategoria(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('evento', 'categoria')


class MemoriaEvento(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='memorias'
    )
    titulo = models.CharField(max_length=255)

    # ✅ Archivo memoria (PDF, ZIP, etc.)
    archivo = CloudinaryField(
        'archivo_memoria',
        resource_type='raw',
        folder='eventos/memorias',
        blank=True,
        null=True
    )

    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.evento.eve_nombre})"


class Proyecto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_proyecto = models.CharField(max_length=200)
    descripcion_proyecto = models.TextField()

    creador = models.ForeignKey(
        "app_usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="proyectos_creados"
    )

    participantes = models.ManyToManyField(
        "app_usuarios.Usuario",
        related_name="proyectos_participantes",
        blank=True
    )

    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="proyectos",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre_proyecto} ({self.id})"
