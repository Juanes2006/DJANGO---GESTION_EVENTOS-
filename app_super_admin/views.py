from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app_eventos.models import Evento
from app_super_admin.models import Area, Categoria
from app_admin.models import AdministradorEvento
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required



@login_required
def ver_evento_superadmin(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)

    # accediendo al administrador relacionado
    administrador = evento.adm_id  # Esto ya es una instancia de AdministradorEvento

    context = {
        "evento": evento,
        "administrador": administrador,
    }
    return render(request, "app_super_admin/detalle_evento_superadmin.html", context)

@login_required
def super_admin(request):
    if request.method == "POST":
        pass
    eventos = Evento.objects.all()
    return render(request, "app_super_admin/super_admin.html", {"eventos": eventos})
@login_required
def eventos_superadmin(request):
    eventos = Evento.objects.all()
    return render(request, "app_super_admin/super_admin.html", {"eventos": eventos})
@login_required
def ver_evento_superadmin(request, eve_id):
    # Suponiendo que el modelo Evento tiene un campo ForeignKey llamado 'creado_por' que apunta al modelo User
    evento = get_object_or_404(Evento, pk=eve_id)
    # Obtener el 
    administrador = evento.adm_id  # Esto ya es una instancia de AdministradorEvento

    # Puedes pasar los administradores al template
    
    return render(request, "app_super_admin/detalle_evento_superadmin.html", {"evento": evento, "administrador": administrador})
@login_required
def agregar_area(request):
    if request.method == "POST":
        are_nombre = request.POST.get("are_nombre")
        are_descripcion = request.POST.get("are_descripcion")
        nueva_area = Area(are_nombre=are_nombre, are_descripcion=are_descripcion)
        nueva_area.save()
        messages.success(request, f"Área '{are_nombre}' agregada exitosamente.")
        return redirect("super_admin:agregar_area")
    return render(request, "app_super_admin/agregar_area.html")
@login_required
def agregar_categoria(request):
    if request.method == "POST":
        cat_nombre = request.POST.get("cat_nombre")
        cat_descripcion = request.POST.get("cat_descripcion")
        cat_area_fk = request.POST.get("cat_area_fk")
        area = get_object_or_404(Area, pk=cat_area_fk)
        nueva_categoria = Categoria(
            cat_nombre=cat_nombre,
            cat_descripcion=cat_descripcion,
            cat_area_fk=area
        )
        nueva_categoria.save()
        messages.success(request, f"Categoría '{cat_nombre}' agregada exitosamente al área.")
        return redirect("super_admin:agregar_categoria")
    areas = Area.objects.all()
    return render(request, "app_super_admin/agregar_categoria.html", {"areas": areas})



import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


from django.contrib.auth.hashers import make_password

# views.py
@login_required
def panel_aprobaciones_view(request):
    solicitudes = AdministradorEvento.objects.filter(aprobado=False)
    return render(request, 'app_super_admin/panel_aprobacion.html', {"solicitudes": solicitudes})

@login_required
def aprobar_admin(request, admin_id):
    admin_evento = get_object_or_404(AdministradorEvento, id=admin_id)
    usuario = admin_evento.usuario

    # ✅ Generar nueva contraseña aleatoria segura
    nueva_contrasena = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    
    # ✅ Actualizar datos del usuario
    usuario.username = usuario.email  # usar el correo como usuario
    usuario.password = make_password(nueva_contrasena)
    usuario.save()

    # ✅ Marcar como aprobado
    admin_evento.aprobado = True
    admin_evento.save()

    # ✅ Enviar correo con credenciales
    asunto = "🎉 Aprobación como Administrador de Eventos"
    mensaje = (
        f"Hola {usuario.first_name},\n\n"
        f"Tu solicitud para ser administrador ha sido aprobada.\n"
        f"Ya puedes iniciar sesión en el sistema con las siguientes credenciales:\n\n"
        f"🔐 Usuario: {usuario.email}\n"
        f"🔑 Contraseña: {nueva_contrasena}\n\n"
        f"Por favor, cambia tu contraseña después de iniciar sesión.\n\n"
        f"Saludos,\nEquipo de Eventos"
    )

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,  # asegúrate de tenerlo configurado en settings.py
        [usuario.email],
        fail_silently=False,
    )

    messages.success(request, f"✅ {usuario.username} fue aprobado y notificado por correo.")
    return redirect('main:panel_aprobaciones')
