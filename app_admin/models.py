from django.db import models
from app_usuarios.models import Usuario

class AdministradorEvento(models.Model):
    
    
    ### nuevo acampo para relacionar con Usuario
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def _str_(self):
        return f"AdminEvento: {self.usuario.username}"


    
    