
# Create your views here.
# app_eventos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app_eventos.models import Evento, MemoriaEvento
from app_super_admin.models import Categoria
from app_eventos.models import EventoCategoria
from app_admin.models import  AdministradorEvento
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.models import User

def crear_evento(request):
    categorias = Categoria.objects.all()

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        ciudad = request.POST.get("ciudad")
        lugar = request.POST.get("lugar")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        cobro = request.POST.get("cobro", "No")
        cupos = request.POST.get("cupos") or None
        categoria_id = request.POST.get("categorias")

        imagen = request.FILES.get("imagen")
        archivo_pdf = request.FILES.get("archivo_programacion")

        # Administrador ficticio o por defecto
        try:
            admin_asignado = AdministradorEvento.objects.get(usuario=request.user)
        except AdministradorEvento.DoesNotExist:
            messages.error(request, "Tu cuenta no está registrada como administrador.")
            return redirect("main:login")

        # Guardar archivos
        imagen_nombre = imagen.name if imagen else ""
        archivo_pdf_nombre = archivo_pdf.name if archivo_pdf else ""

        # Crear evento
        evento = Evento.objects.create(
            eve_nombre=nombre,
            eve_descripcion=descripcion,
            eve_ciudad=ciudad,
            eve_lugar=lugar,
            eve_fecha_inicio=fecha_inicio,
            eve_fecha_fin=fecha_fin,
            eve_estado="CREADO",
            adm_id=admin_asignado,
            cobro=cobro,
            cupos=cupos,
            imagen=imagen_nombre,
            archivo_programacion=archivo_pdf_nombre
        )

        # Relacionar con categoría
        if categoria_id:
            EventoCategoria.objects.create(evento=evento, categoria_id=categoria_id)

        # Guardar archivos en media
        if imagen:
            with open(f"static/imagenes/{imagen_nombre}", 'wb+') as destination:
                for chunk in imagen.chunks():
                    destination.write(chunk)

        if archivo_pdf:
            with open(f"static/programacion/{archivo_pdf_nombre}", 'wb+') as destination:
                for chunk in archivo_pdf.chunks():
                    destination.write(chunk)
                    
                    
        superadmins = User.objects.filter(is_superuser=True)
        correos_superadmin = [user.email for user in superadmins if user.email]

        # Enviar correo
        if correos_superadmin:
            asunto = "🔔 Nuevo evento creado"
            mensaje = f"""
        Hola,

        El administrador {request.user.username} ha creado un nuevo evento:

        📌 Nombre: {evento.eve_nombre}
        📍 Lugar: {evento.eve_ciudad} - {evento.eve_lugar}
        📅 Fechas: {evento.eve_fecha_inicio} al {evento.eve_fecha_fin}
        🔗 Verifica desde el panel de administración.

        Saludos,
        Sistema de Eventos
        """
            send_mail(
                asunto,
                mensaje,
                "tucorreo@gmail.com",  
                correos_superadmin,    
                fail_silently=False,
            )


        messages.success(request, f"¡Se ha creado el evento {evento.eve_nombre}!")
        return redirect("admin_evento:ventana")  # Ajusta según tu namespace
    
    
        

       

    return render(request, "app_eventos/crear_evento.html", {
        "categorias": categorias
    })
##################################################################
def editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == "POST":
        evento.eve_nombre = request.POST.get("nombre")
        evento.eve_descripcion = request.POST.get("descripcion")
        evento.eve_ciudad = request.POST.get("ciudad")
        evento.eve_lugar = request.POST.get("lugar")

        # Manejo de fechas
        fecha_inicio_str = request.POST.get("fecha_inicio")
        fecha_fin_str = request.POST.get("fecha_fin")

        try:
            evento.eve_fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d") if fecha_inicio_str else None
        except ValueError:
            messages.error(request, "Fecha de inicio inválida")
            return render(request, "app_eventos/editar_evento.html", {"evento": evento})

        try:
            evento.eve_fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d") if fecha_fin_str else None
        except ValueError:
            messages.error(request, "Fecha fin inválida")
            return render(request, "app_eventos/editar_evento.html", {"evento": evento})

        evento.cobro = request.POST.get("cobro")

        # Procesar imagen
        imagen = request.FILES.get("imagen")
        if imagen:
            imagen_nombre = imagen.name
            with open(f"static/imagenes/{imagen_nombre}", 'wb+') as destination:
                for chunk in imagen.chunks():
                    destination.write(chunk)
            evento.imagen = f"{imagen_nombre}"

        # Procesar archivo PDF
        archivo_pdf = request.FILES.get("archivo_programacion")
        if archivo_pdf:
            archivo_pdf_nombre = archivo_pdf.name
            with open(f"static/programacion/{archivo_pdf_nombre}", 'wb+') as destination:
                for chunk in archivo_pdf.chunks():
                    destination.write(chunk)
            evento.archivo_programacion = f"{archivo_pdf_nombre}"

        evento.save()
        messages.success(request, "Evento editado con éxito.")
        return redirect("main:lista_eventos")


    # GET request
    return render(request, "app_eventos/editar_evento.html", {"evento": evento})

#################################################################

from django.http import FileResponse, Http404
import os
from django.conf import settings

def descargar_programacion(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if not evento.archivo_programacion:
        messages.error(request, "No hay archivo de programación disponible para este evento.")
        return redirect("superadmin:super_adm")

    filepath = evento.archivo_programacion.path
    if not os.path.exists(filepath):
        raise Http404("Archivo no encontrado")
    
    return FileResponse(open(filepath, 'rb'), as_attachment=True)
#######################################

def cancelar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    evento.eve_estado = "CANCELADO"
    evento.save()
    messages.success(request, f"Evento {evento.eve_nombre} cancelado exitosamente.")
    return redirect("admin:ventana")

def activar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    evento.eve_estado = "ACTIVO"
    evento.save()
    messages.success(request, f"Evento {evento.eve_nombre} activado exitosamente.")
    return redirect("superadmin:eventos_superadmin")

def desactivar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    evento.eve_estado = "INACTIVO"
    evento.save()
    messages.success(request, f"Evento {evento.eve_nombre} desactivado exitosamente.")
    return redirect("superadmin:eventos_superadmin")

def eliminar_evento(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)
    evento.delete()
    messages.success(request, f"Evento {evento.eve_nombre} eliminado exitosamente.")
    return redirect("superadmin:eventos_superadmin")  # Ajusta según tu namespace




def subir_memoria_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == 'POST':
        titulo_base = request.POST.get('titulo') 
        archivos = request.FILES.getlist('archivos') 

        if not titulo_base or not archivos:
            messages.error(request, "Debes llenar todos los campos.")
        else:
            for index, archivo in enumerate(archivos, start=1):
                MemoriaEvento.objects.create(
                    evento=evento,
                    titulo=f"{titulo_base} #{index}" if len(archivos) > 1 else titulo_base,
                    archivo=archivo
                )

            messages.success(request, f"{len(archivos)} archivo(s) subido(s) exitosamente.")
            return redirect('eventos:subir_memoria_evento', evento_id=int(evento_id))

    return render(request, 'app_eventos/subir_memoria.html', {'evento': evento})

def consultar_memorias(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    memorias = MemoriaEvento.objects.filter(evento=evento)

    return render(request, 'app_eventos/consultar_memorias.html', {
        'evento': evento,
        'memorias': memorias
    })

def eliminar_memoria(request, memoria_id):
    print("[LOG] Ingresando a eliminar_memoria con ID:", memoria_id)

    if request.method == 'POST':
        deleted_count, _ = MemoriaEvento.objects.filter(pk=memoria_id).delete()
        print("[LOG] Registros eliminados:", deleted_count)

        if deleted_count:
            messages.success(request, "✅ Memoria eliminada correctamente.")
        else:
            messages.warning(request, "⚠ No se encontró la memoria para eliminar.")

        evento_id = request.POST.get("evento_id")
        print("[LOG] evento_id recibido desde POST:", evento_id)

        if evento_id:
            return redirect('eventos:consultar_memorias', evento_id=int(evento_id))
        else:
            return redirect('admin_evento:ventana') 

    return redirect('eventos:lista_eventos')
