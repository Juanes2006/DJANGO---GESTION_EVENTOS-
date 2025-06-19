from django.db import models
from app_usuarios.models import Usuario


class SuperAdmin(models.Model):
    
    #### NUEVO CAMPO PARA RELACIONAR CON USUARIO ####
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def _str_(self):
        return f"Super Admin: {self.usuario.username}"



class Area(models.Model):
    are_codigo = models.AutoField(primary_key=True)
    are_nombre = models.CharField(max_length=45)
    are_descripcion = models.CharField(max_length=400)

    def __str__(self):
        return self.are_nombre

class Categoria(models.Model):
    cat_codigo = models.AutoField(primary_key=True)
    cat_nombre = models.CharField(max_length=45)
    cat_descripcion = models.CharField(max_length=400)
    cat_area_fk = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='categorias')

    def __str__(self):
        return self.cat_nombre
