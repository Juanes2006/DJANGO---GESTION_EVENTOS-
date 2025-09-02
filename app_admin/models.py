from django.db import models
from app_usuarios.models import Usuario

class AdministradorEvento(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    aprobado = models.BooleanField(default=False)
    limite_eventos = models.PositiveIntegerField(default=3)  
    activo = models.BooleanField(default=True)  



    def __str__(self):
        return f"AdminEvento: {self.usuario.username} - {'Aprobado' if self.aprobado else 'Pendiente'}"


class PlantillaCertificado(models.Model):
    nombre = models.CharField(max_length=100, default="Plantilla por defecto")
    titulo = models.CharField(max_length=100, default="🎓 CERTIFICADO")
    subtitulo = models.CharField(max_length=200, default="Se otorga el presente certificado a")
    color_titulo = models.CharField(max_length=20, default="#00008B")
    color_nombre = models.CharField(max_length=20, default="#8B0000")
    mostrar_firma = models.BooleanField(default=True)
    texto_firma = models.CharField(max_length=100, default="Coordinador del Evento")
    pos_titulo_y = models.FloatField(default=4.0)
    pos_nombre_y = models.FloatField(default=8.0)
    logo = models.ImageField(upload_to='certificados/logos/', null=True, blank=True)
    sello = models.ImageField(upload_to='certificados/sellos/', null=True, blank=True)


    def __str__(self):
        return self.nombre