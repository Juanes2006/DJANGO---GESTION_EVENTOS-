from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app_eventos.models import Evento
from app_super_admin.models import Area, Categoria
from app_admin.models import AdministradorEvento
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

def ver_evento_superadmin(request, eve_id):
    evento = get_object_or_404(Evento, pk=eve_id)

    # accediendo al administrador relacionado
    administrador = evento.adm_id  # Esto ya es una instancia de AdministradorEvento

    context = {
        "evento": evento,
        "administrador": administrador,
    }
    return render(request, "app_super_admin/detalle_evento_superadmin.html", context)


def super_admin(request):
    if request.method == "POST":
        pass
    eventos = Evento.objects.all()
    return render(request, "app_super_admin/super_admin.html", {"eventos": eventos})

def eventos_superadmin(request):
    eventos = Evento.objects.all()
    return render(request, "app_super_admin/super_admin.html", {"eventos": eventos})

def ver_evento_superadmin(request, eve_id):
    # Suponiendo que el modelo Evento tiene un campo ForeignKey llamado 'creado_por' que apunta al modelo User
    evento = get_object_or_404(Evento, pk=eve_id)
    # Obtener el 
    administrador = evento.adm_id  # Esto ya es una instancia de AdministradorEvento

    # Puedes pasar los administradores al template
    
    return render(request, "app_super_admin/detalle_evento_superadmin.html", {"evento": evento, "administrador": administrador})

def agregar_area(request):
    if request.method == "POST":
        are_nombre = request.POST.get("are_nombre")
        are_descripcion = request.POST.get("are_descripcion")
        nueva_area = Area(are_nombre=are_nombre, are_descripcion=are_descripcion)
        nueva_area.save()
        messages.success(request, f"Área '{are_nombre}' agregada exitosamente.")
        return redirect("super_admin:agregar_area")
    return render(request, "app_super_admin/agregar_area.html")

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
