from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)
    roles = (
        ('SUPER_ADMINISTRADOR', 'Super Administrador'),
        ('ADMINISTRADOR', 'Administrador'),
        ('EVALUADOR', 'Evaluador'),
        ('PARTICIPANTE', 'Participante'),
        ('ASISTENTE', 'Asistente'),
    )
    rol = models.CharField(max_length=30, choices=roles, default='PARTICIPANTE')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UsuarioManager()

    def _str_(self):
        return f"{self.username} ({self.rol})"

