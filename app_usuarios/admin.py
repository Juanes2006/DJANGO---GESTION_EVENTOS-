from django.contrib import admin
from app_usuarios.models import Usuario
from django.contrib.auth.admin import UserAdmin
from app_registros.models import Asistentes
from app_admin.models import AdministradorEvento
from app_evaluadores.models import Evaluador
from app_participantes.models import Participantes
from app_super_admin.models import SuperAdmin



class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'email', 'rol', 'is_active', 'is_staff')
    search_fields = ('email', 'username',)
    ordering = ('email',)

    readonly_fields = ('last_login', 'date_joined') 

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'rol')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),  
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2', 'rol',
                'is_staff', 'is_superuser', 'is_active'
            )}
        ),
    )
    
    
    def save_model(self, request, obj, form, change):
    # Verificar si está intentando crear un nuevo SUPER_ADMINISTRADOR
        if obj.rol == 'SUPER_ADMINISTRADOR':
            existe_superadmin = Usuario.objects.filter(rol='SUPER_ADMINISTRADOR').exclude(pk=obj.pk).exists()
            if existe_superadmin:
                self.message_user(request, "❌ Ya existe un SUPER_ADMINISTRADOR en el sistema. No se pueden crear más.", level="error")
                return  # Evita guardar

        # Guardar el usuario
        super().save_model(request, obj, form, change)

        try:
            if obj.rol == 'ADMINISTRADOR' and not AdministradorEvento.objects.filter(usuario=obj).exists():
                AdministradorEvento.objects.create(usuario=obj)
            elif obj.rol == 'SUPER_ADMINISTRADOR' and not SuperAdmin.objects.filter(usuario=obj).exists():
                SuperAdmin.objects.create(usuario=obj)
            elif obj.rol == 'EVALUADOR' and not Evaluador.objects.filter(usuario=obj).exists():
                Evaluador.objects.create(usuario=obj)
            elif obj.rol == 'PARTICIPANTE' and not Participantes.objects.filter(usuario=obj).exists():
                Participantes.objects.create(usuario=obj)
            elif obj.rol == 'ASISTENTE' and not Asistentes.objects.filter(usuario=obj).exists():
                Asistentes.objects.create(usuario=obj)
        except Exception as e:
            self.message_user(request, f"⚠️ Error al asignar rol: {e}", level="error")

admin.site.register(SuperAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Asistentes)
admin.site.register(AdministradorEvento)
admin.site.register(Evaluador)
admin.site.register(Participantes)
