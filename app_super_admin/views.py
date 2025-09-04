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
    areas = Area.objects.all()  # Filtra si quieres solo activas: Area.objects.filter(activo=True)

    return render(request, "app_super_admin/super_admin.html", {"eventos": eventos, "areas": areas})
@login_required
def eventos_superadmin(request):
    eventos = Evento.objects.all()
    areas = Area.objects.all()  # Filtra si quieres solo activas: Area.objects.filter(activo=True)

    return render(request, "app_super_admin/super_admin.html", {"eventos": eventos, "areas": areas})
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
        return redirect("super_admin:eventos_superadmin")
    return render(request, "app_super_admin/super_admin.html")

@login_required
def agregar_categoria(request):
    print("➡️ Entró a la vista agregar_categoria")  # Log inicial

    if request.method == "POST":
        print("✅ Se recibió un POST")
        print("📩 Datos recibidos:", request.POST)

        cat_nombre = request.POST.get("cat_nombre")
        cat_descripcion = request.POST.get("cat_descripcion")
        cat_area_fk = request.POST.get("cat_area_fk")

        print(f"📝 Nombre: {cat_nombre}")
        print(f"📝 Descripción: {cat_descripcion}")
        print(f"📝 Área ID: {cat_area_fk}")

        try:
            area = get_object_or_404(Area, pk=cat_area_fk)
            print(f"✅ Área encontrada: {area.are_nombre}")
        except Exception as e:
            print(f"❌ Error buscando el área con ID {cat_area_fk}: {e}")
            messages.error(request, "No se pudo encontrar el área seleccionada.")
            return redirect("super_admin:eventos_superadmin")

        try:
            nueva_categoria = Categoria(
                cat_nombre=cat_nombre,
                cat_descripcion=cat_descripcion,
                cat_area_fk=area
            )
            nueva_categoria.save()
            print("✅ Categoría guardada correctamente")
            messages.success(request, f"Categoría '{cat_nombre}' agregada exitosamente al área.")
        except Exception as e:
            print(f"❌ Error al guardar la categoría: {e}")
            messages.error(request, "Hubo un error al guardar la categoría.")
        
        return redirect("super_admin:eventos_superadmin")

    else:
        print("ℹ️ Request no es POST (es GET probablemente)")

    areas = Area.objects.all()
    print(f"📊 Áreas disponibles: {areas.count()}")
    return render(request, "app_super_admin/super_admin.html", {"areas": areas})

import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


from django.contrib.auth.hashers import make_password

# views.py
@login_required
def panel_aprobaciones_view(request):
    solicitudes = AdministradorEvento.objects.all()
    return render(request, 'app_super_admin/panel_aprobacion.html', {"solicitudes": solicitudes})
@login_required
def cambiar_estado_admin(request, admin_id):
    admin_evento = get_object_or_404(AdministradorEvento, id=admin_id)
    admin_evento.activo = not admin_evento.activo
    admin_evento.save()
    messages.success(request, f"✅ Estado de {admin_evento.usuario.username} actualizado correctamente.")
    return redirect('superadmin:panel_aprobaciones')

@login_required
def aprobar_admin(request, admin_id):
    admin_evento = get_object_or_404(AdministradorEvento, id=admin_id)
    usuario = admin_evento.usuario

    if request.method == "POST":
        # Limite de eventos
        limite = request.POST.get("limite_eventos", 3)
        try:
            limite = int(limite)
            if limite < 1:
                limite = 1
        except ValueError:
            limite = 3

        # Checkbox activo
        activo = request.POST.get("activo")
        if activo is None:
            activo = True
        else:
            activo = activo == "on"

        # Generar contraseña SOLO la primera vez que se aprueba
        if not admin_evento.aprobado:
            nueva_contrasena = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            usuario.username = usuario.email
            usuario.password = make_password(nueva_contrasena)
            usuario.save()

            # Enviar correo
            asunto = "🎉 Aprobación como Administrador de Eventos"
            mensaje = (
                f"Hola {usuario.first_name},\n\n"
                f"Tu solicitud para ser administrador ha sido aprobada.\n"
                f"Ya puedes iniciar sesión en el sistema con las siguientes credenciales:\n\n"
                f"🔐 Usuario: {usuario.email}\n"
                f"🔑 Contraseña: {nueva_contrasena}\n\n"
                f"Límite de eventos: {limite}\n"
                f"Activo: {'Sí' if activo else 'No'}\n\n"
                f"Por favor, cambia tu contraseña después de iniciar sesión.\n\n"
                f"Saludos,\nEquipo de Eventos"
            )

            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
            )

        # Actualizar campos
        admin_evento.aprobado = True
        admin_evento.limite_eventos = limite
        admin_evento.activo = activo
        admin_evento.save()

        messages.success(request, f"✅ {usuario.username} aprobado/actualizado correctamente.")
        return redirect('superadmin:panel_aprobaciones')

    messages.info(request, "❗ Acción no válida sin formulario.")
    return redirect('superadmin:panel_aprobaciones')