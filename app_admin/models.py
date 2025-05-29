from django.db import models

class AdministradorEvento(models.Model):
    adm_id = models.CharField(primary_key=True, max_length=20)
    adm_nombre = models.CharField(max_length=100)
    adm_correo = models.CharField(max_length=100)
    adm_telefono = models.CharField(max_length=45)

    def __str__(self):
        return self.adm_nombre
