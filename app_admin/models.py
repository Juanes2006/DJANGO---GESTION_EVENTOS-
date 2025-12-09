from django.db import models
from app_usuarios.models import Usuario


class AdministradorEvento(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="administrador_evento"
    )
    aprobado = models.BooleanField(default=False)
    limite_eventos = models.PositiveIntegerField(default=3)
    activo = models.BooleanField(default=True)

    def __str__(self):
        if self.usuario:
            return f"AdminEvento: {self.usuario.username} - {'Aprobado' if self.aprobado else 'Pendiente'}"
        return "AdminEvento: Sin usuario"


# =======================


FUENTES = [
    ("Helvetica", "Helvetica"),
    ("Helvetica-Bold", "Helvetica Bold"),
    ("Times-Roman", "Times"),
    ("Courier", "Courier"),
]


class PlantillaCertificado(models.Model):
    nombre = models.CharField(max_length=100)

    # Textos fijos editables
    titulo = models.CharField(
        max_length=255,
        default="CERTIFICADO DE PARTICIPACIÓN",
        blank=True
    )
    subtitulo = models.CharField(
        max_length=255,
        default="Se otorga el presente certificado a",
        blank=True
    )
    texto_firma = models.CharField(
        max_length=255,
        default="Coordinador del Evento",
        blank=True
    )

    # Estilos
    color_fondo = models.CharField(max_length=7, default="#FFFFFF", blank=True)
    color_borde = models.CharField(max_length=7, default="#000000", blank=True)
    color_titulo = models.CharField(max_length=7, default="#000000", blank=True)
    color_nombre = models.CharField(max_length=7, default="#000000", blank=True)

    fuente_titulo = models.CharField(
        max_length=50,
        choices=FUENTES,
        default="Helvetica-Bold",
        blank=True
    )
    tamano_titulo = models.IntegerField(default=28, blank=True)

    fuente_nombre = models.CharField(
        max_length=50,
        choices=FUENTES,
        default="Helvetica-Bold",
        blank=True
    )
    tamano_nombre = models.IntegerField(default=24, blank=True)

    borde_grosor = models.IntegerField(default=3, blank=True)
    borde_margen = models.IntegerField(default=50, blank=True)

    # Imágenes
    logo = models.ImageField(
        upload_to="certificados/logos/",
        blank=True,
        null=True
    )
    sello = models.ImageField(
        upload_to="certificados/sellos/",
        blank=True,
        null=True
    )
    firma = models.ImageField(
        upload_to="certificados/firmas/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nombre
