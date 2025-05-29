
# Create your views here.
# app_eventos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app_eventos.models import Evento
from app_super_admin.models import Categoria
from app_eventos.models import EventoCategoria
from app_admin.models import  AdministradorEvento
from datetime import datetime

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
        administradores = AdministradorEvento.objects.all()
        if administradores.exists():
            admin_asignado = min(administradores, key=lambda adm: adm.eventos.count())
        else:
            admin_asignado = AdministradorEvento.objects.create(
                adm_id="admin1",
                adm_nombre="Admin Demo",
                adm_correo="demo@admin.com",
                adm_telefono="123456"
            )


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
