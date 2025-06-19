from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q, Count
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import mark_safe
from django.db import transaction
from app_eventos.models import Evento
from app_super_admin.models import Area, Categoria
from app_participantes.models import Participantes, ParticipantesEventos
from app_registros.models import Asistentes, AsistentesEventos
from app_evaluadores.models import Criterio, Instrumento, Calificacion, Evaluador, EvaluadorEventos
from django.utils.timezone import now

import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.conf import settings

from app_usuarios.models import Usuario

import csv
import io
from collections import defaultdict

app_name = 'app_admin'



def ventana(request):
    """Vista principal del administrador de eventos"""
    eventos = Evento.objects.all()
    return render(request, 'app_admin/administrador_evento.html', {'eventos': eventos})
###################################

def gestionar_inscripciones(request, eve_id):
    """Gestionar inscripciones de participantes"""
    evento = get_object_or_404(Evento, pk=eve_id)
    
    # Query similar to the Flask SQLAlchemy join
    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=eve_id
    ).select_related('par_eve_participante_fk__usuario')
    
    participantes = []
    for pe in participantes_eventos:
        asistente = pe.par_eve_participante_fk  # instancia de Asistentes
        usuario = asistente.usuario
        participantes.append({
            'id': usuario.id,
            
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'par_estado': pe.par_estado,
            'par_eve_documentos': pe.par_eve_documentos,
        })
    
    return render(request, "app_admin/gestionar_inscripciones.html", {
        'evento': evento,
        'participantes': participantes
    })


def gestionar_inscripcion_asis(request, eve_id):
    """Gestionar inscripciones de asistentes"""
    evento = get_object_or_404(Evento, pk=eve_id)

    asistentes_eventos = AsistentesEventos.objects.filter(
    asi_eve_evento_fk=evento
).select_related("asi_eve_asistente_fk__usuario")

    asistentes = []
    for ae in asistentes_eventos:
        asistente = ae.asi_eve_asistente_fk  # instancia de Asistentes
        usuario = asistente.usuario  # instancia de Usuario relacionado

        asistentes.append({
            'id': usuario.id,
            
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'asi_eve_estado': ae.asi_eve_estado,
            'asi_eve_soporte': ae.asi_eve_soporte,
        })

    return render(request, "app_admin/gestionar_inscripciones_asis.html", {
        'evento': evento,
        'asistentes': asistentes
    })
    
def gestionar_evaluadores(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    evaluadores_eventos = EvaluadorEventos.objects.filter(
        eva_eve_evento_fk=evento_id
    ).select_related('eva_eve_evaluador_fk')

    evaluadores = []
    for ee in evaluadores_eventos:
        asistente = ee.eva_eve_evaluador_fk  # instancia de Asistentes
        usuario = asistente.usuario 
        evaluadores.append({
            'id': usuario.id,
            
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'eva_eve_estado': ee.eva_estado,
            'eva_eve_documentos': ee.eva_eve_documentos,
        })

    return render(request, "app_admin/gestionar_evaluadores.html", {
        'evento': evento,
        'evaluadores': evaluadores
    })


##############################################

def generar_qr_contenido(contenido, nombre_archivo='qr.png'):
    img = qrcode.make(contenido)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return ContentFile(buffer.read(), name=nombre_archivo)

import random
import string

def generar_contrasena(longitud=10):
    """Genera una contraseña aleatoria segura"""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(caracteres, k=longitud))


def actualizar_estado(request):
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    usuario_id = request.POST.get('usuario_id')
    evento_id = request.POST.get('evento_id')
    nuevo_estado = request.POST.get('estado')
    print("📥 Datos recibidos:")
    print("Usuario ID:", usuario_id)
    print("Evento ID:", evento_id)
    print("Nuevo Estado:", nuevo_estado)
    if not usuario_id or not evento_id or not nuevo_estado:
        messages.error(request, "Faltan datos para actualizar el estado.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    usuario = get_object_or_404(Usuario, pk=usuario_id)
    evento = get_object_or_404(Evento, pk=evento_id)

    nombre = f"{usuario.first_name} {usuario.last_name}"
    correo = usuario.email
    asunto = f"Estado actualizado - Evento {evento.eve_nombre}"
    mensaje = f"Hola {nombre},\n\nSu estado ha sido actualizado a: {nuevo_estado}."
    clave = "EVT" + str(evento.pk).zfill(5)

    try:
        if usuario.rol == 'PARTICIPANTE':
            participante, _ = Participantes.objects.get_or_create(usuario=usuario)
            participante_evento, creado = ParticipantesEventos.objects.get_or_create(
                par_eve_participante_fk=participante,
                par_eve_evento_fk=evento,
                defaults={
                    'par_estado': nuevo_estado,
                    'par_eve_clave': clave,
                    'par_eve_fecha_hora': now()
                }
            )
            if not creado:
                participante_evento.par_estado = nuevo_estado
                participante_evento.save()
                
            print("Evaluador:", evaluador.id, "Evento:", evento.id, "Estado:", nuevo_estado)


            if nuevo_estado == "ACEPTADO":
                nueva_password = generar_contrasena()
                usuario.set_password(nueva_password)
                usuario.save()
                qr_contenido = f"Participante: {nombre}\nClave: {clave}\nEvento ID: {evento.eve_id}"
                qr_img = generar_qr_contenido(qr_contenido)
                mensaje +=f"Hola {usuario.first_name},\n\nHas sido aceptado como Participante en el evento.\n\nTus credenciales:\nUsuario: {usuario.email}\nContraseña: {nueva_password}\n\nPor favor cambia tu contraseña después de iniciar sesión."
                email = EmailMessage(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
                email.attach('qr_participante.png', qr_img.read(), 'image/png')
                email.send()
            else:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])

        elif usuario.rol == 'EVALUADOR':
            evaluador, _ = Evaluador.objects.get_or_create(usuario=usuario)
            evaluador_evento, creado = EvaluadorEventos.objects.get_or_create(
                eva_eve_evaluador_fk=evaluador,
                eva_eve_evento_fk=evento,
                defaults={
                    'eva_estado': nuevo_estado,
                    'eva_eve_clave': clave,
                    'eva_eve_fecha_hora': now()
                    
                }
            
            )
            
            
            if not creado:
                evaluador_evento.eva_estado = nuevo_estado
                evaluador_evento.save()

            if nuevo_estado == "ACEPTADO":
                nueva_password = generar_contrasena()
                usuario.set_password(nueva_password)
                usuario.save()
                qr_contenido = f"Evaluador: {nombre}\nClave: {clave}\nEvento ID: {evento.eve_id}"
                qr_img = generar_qr_contenido(qr_contenido)
                mensaje +=f"Hola {usuario.first_name},\n\nHas sido aceptado como Evaluador en el evento.\n\nTus credenciales:\nUsuario: {usuario.email}\nContraseña: {nueva_password}\n\nPor favor cambia tu contraseña después de iniciar sesión."
                email = EmailMessage(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
                email.attach('qr_evaluador.png', qr_img.read(), 'image/png')
                email.send()
            else:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])

        elif usuario.rol == 'ASISTENTE':
            asistente, _ = Asistentes.objects.get_or_create(usuario=usuario)
            asistente_evento, creado = AsistentesEventos.objects.get_or_create(
                asi_eve_asistente_fk=asistente,
                asi_eve_evento_fk=evento,
                defaults={
                    'asi_eve_estado': nuevo_estado,
                    'asi_eve_fecha_hora': now()
                }
            )
            if not creado:
                asistente_evento.asi_eve_estado = nuevo_estado
                asistente_evento.save()

            if nuevo_estado == "ACEPTADO":
                nueva_password = generar_contrasena()
                usuario.set_password(nueva_password)
                usuario.save()
                qr_contenido = f"Asistente: {nombre}\nEvento ID: {evento.eve_id}\nEstado: {nuevo_estado}"
                qr_img = generar_qr_contenido(qr_contenido)
                mensaje +=f"Hola {usuario.first_name},\n\nHas sido aceptado como Asistente en el evento.\n\nTus credenciales:\nUsuario: {usuario.email}\nContraseña: {nueva_password}\n\nPor favor cambia tu contraseña después de iniciar sesión."
                email = EmailMessage(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
                email.attach('qr_asistente.png', qr_img.read(), 'image/png')
                email.send()
            else:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
        else:
            messages.error(request, "Rol no válido.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        messages.success(request, "Estado actualizado correctamente y correo enviado.")
        return redirect('main:lista_eventos')

    except Exception as e:
        messages.error(request, f"Error al actualizar el estado: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))

def ver_estadisticas(request):
    """Ver estadísticas de eventos"""
    eventos = Evento.objects.all()
    estadisticas = []

    for evento in eventos:
        total_asistentes = AsistentesEventos.objects.filter(asi_eve_evento_fk=evento.eve_id).count()
        total_participantes = ParticipantesEventos.objects.filter(par_eve_evento_fk=evento.eve_id).count()
        total = total_asistentes + total_participantes
        
        porcentaje_participantes = (total_participantes / total * 100) if total > 0 else 0

        estadisticas.append({
            'evento_id': evento.eve_id,
            'evento_nombre': evento.eve_nombre,
            'asistentes': total_asistentes,
            'participantes': total_participantes,
            'total': total,
            'porcentaje_participantes': porcentaje_participantes
        })

    return render(request, 'app_admin/estadisticas.html', {'estadisticas': estadisticas})


def toggle_inscripcion(request, evento_id, tipo):
    """Alternar estado de inscripciones"""
    evento = get_object_or_404(Evento, pk=evento_id)

    if tipo == "participantes":
        evento.inscripciones_participantes_abiertas = not evento.inscripciones_participantes_abiertas
    elif tipo == "asistentes":
        evento.inscripciones_asistentes_abiertas = not evento.inscripciones_asistentes_abiertas
        
    elif tipo == "evaluadores":
        evento.inscripciones_evaluadores_abiertas = not evento.inscripciones_evaluadores_abiertas
    else:
        messages.error(request, "Tipo de inscripción no válido.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    evento.save()
    messages.success(request, "Estado de inscripciones actualizado correctamente.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def cargar_instrumentos(request):
    """Cargar instrumentos de evaluación"""
    if request.method == 'POST':
        tipo_instrumento = request.POST.get('tipo_instrumento')
        descripcion_instrumento = request.POST.get('descripcion_instrumento')
        evento_id = request.POST.get('evento_id')
        
        if tipo_instrumento and descripcion_instrumento and evento_id:
            evento = get_object_or_404(Evento, pk=evento_id)
            nuevo_instrumento = Instrumento(
                inst_tipo=tipo_instrumento,
                inst_descripcion=descripcion_instrumento,
                inst_evento_fk=evento
            )
            nuevo_instrumento.save()
            messages.success(request, 'Instrumento cargado correctamente')
        else:
            messages.error(request, 'Debes completar todos los campos')
        
        return redirect('cargar_instrumentos')
    
    instrumentos = Instrumento.objects.all()
    return render(request, 'administrador/cargar_instrumento.html', {'instrumentos': instrumentos})

def gestionar_criterios_admin(request, evento_id):
    """Gestionar criterios de evaluación para un evento"""
    evento = get_object_or_404(Evento, pk=evento_id)
    criterios = Criterio.objects.filter(cri_evento_fk=evento_id)
    instrumento = Instrumento.objects.filter(inst_evento_fk=evento_id).first()
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        peso_str = request.POST.get('peso')

        try:
            peso = float(peso_str) if peso_str else 0
        except ValueError:
            messages.error(request, 'El peso ingresado no es válido.')
            return redirect('gestionar_criterios_admin', evento_id=evento_id)

        if accion == 'crear':
            descripcion = request.POST.get('descripcion')
            suma_actual = Criterio.objects.filter(cri_evento_fk=evento_id).aggregate(
                total=Sum('cri_peso')
            )['total'] or 0

            if suma_actual + peso > 100:
                messages.error(request, f'Error: La suma de los porcentajes no puede superar el 100% (actual: {suma_actual}%, intento agregar: {peso}%).')
                messages.error(request, f'Por favor, ajuste el peso del nuevo criterio, queda por agregar un {100 - suma_actual}%.')
                return redirect('admin_evento:gestionar_criterios_admin', evento_id=evento_id)
            else:
                nuevo_criterio = Criterio(
                    cri_descripcion=descripcion,
                    cri_peso=peso,
                    cri_evento_fk=evento
                )
                nuevo_criterio.save()
                messages.success(request, 'Criterio creado exitosamente.')

        elif accion == 'editar':
            criterio_id = request.POST.get('criterio_id')
            try:
                criterio = Criterio.objects.get(pk=criterio_id)
                suma_sin_este = Criterio.objects.filter(
                    cri_evento_fk=evento_id
                ).exclude(cri_id=criterio.cri_id).aggregate(
                    total=Sum('cri_peso')
                )['total'] or 0

                if suma_sin_este + peso > 100:
                    messages.error(request, f'Error: La suma de los porcentajes no puede superar el 100% (actual sin este: {suma_sin_este}%, intento editar a: {peso}%).')
                    return redirect('admin_evento:gestionar_criterios_admin', evento_id=evento_id)
                else:
                    criterio.cri_descripcion = request.POST.get('descripcion')
                    criterio.cri_peso = peso
                    criterio.save()
                    messages.success(request, 'Criterio actualizado exitosamente.')
            except Criterio.DoesNotExist:
                messages.error(request, 'Criterio no encontrado.')

        elif accion == 'eliminar':
            criterio_id = request.POST.get('criterio_id')
            try:
                criterio = Criterio.objects.get(pk=criterio_id)
                calificaciones_vinculadas = Calificacion.objects.filter(cal_criterio_fk=criterio_id).count()
                if calificaciones_vinculadas > 0:
                    messages.error(request, f'No se puede eliminar el criterio "{criterio.cri_descripcion}" porque tiene {calificaciones_vinculadas} calificación(es) asociada(s).')
                else:
                    criterio.delete()
                    messages.success(request, 'Criterio eliminado exitosamente.')
            except Criterio.DoesNotExist:
                messages.error(request, 'Criterio no encontrado.')

        return redirect('admin_evento:gestionar_criterios_admin', evento_id=evento_id)

    # GET method: calcular total de peso asignado
    total_peso = Criterio.objects.filter(cri_evento_fk=evento_id).aggregate(
        total=Sum('cri_peso')
    )['total'] or 0

    return render(request, 'app_admin/criterios.html', {
        'criterios': criterios,
        'instrumento': instrumento,
        'evento_id': evento_id,
        'total_peso': round(total_peso, 2),
        'evento': evento
    })


def cargar_instrumento_admin(request, evento_id):
    """Cargar instrumento de evaluación para un evento específico"""
    evento = get_object_or_404(Evento, pk=evento_id)
    instrumento_existente = Instrumento.objects.filter(inst_evento_fk=evento_id).first()

    if request.method == 'POST':
        tipo = request.POST['tipo']
        descripcion = request.POST['descripcion']

        if instrumento_existente:
            # Actualizar
            instrumento_existente.inst_tipo = tipo
            instrumento_existente.inst_descripcion = descripcion
            instrumento_existente.save()
            messages.success(request, 'Instrumento actualizado exitosamente.')
        else:
            # Crear
            nuevo_instrumento = Instrumento(
                inst_tipo=tipo,
                inst_descripcion=descripcion,
                inst_evento_fk=evento
            )
            nuevo_instrumento.save()
            messages.success(request, 'Instrumento cargado exitosamente.')

        return redirect('admin_evento:cargar_instrumento_admin', evento_id=evento_id)

    return render(request, 'app_admin/cargar_instrumento.html', {
        'instrumento': instrumento_existente,
        'evento_id': evento_id,
        'evento': evento
    })

def ver_ranking_admin(request, evento_id):
    """Ver ranking de participantes en un evento"""
    evento = get_object_or_404(Evento, pk=evento_id)

    # Django ORM equivalent of the complex query
    from django.db.models import F
    
    ranking_query = Participantes.objects.filter(
        calificacion__cal_criterio_fk__cri_evento_fk=evento_id
    ).annotate(
        puntaje_total=Sum(F('calificacion__cal_valor') * F('calificacion__cal_criterio_fk__cri_peso'))
    ).values(
        'par_id', 'par_nombre', 'puntaje_total'
    ).order_by('-puntaje_total')

    ranking = []
    for item in ranking_query:
        ranking.append({
            'participante_id': item['par_id'],
            'participante_nombre': item['par_nombre'],
            'puntaje_total': item['puntaje_total'] or 0
        })

    return render(request, 'app_admin/ranking.html', {
        'evento': evento,
        'ranking': ranking
    })

def ver_calificaciones_evento(request, evento_id):
    """Ver calificaciones de un evento"""
    evento = get_object_or_404(Evento, pk=evento_id)

    # Participantes que tienen calificaciones asociadas a criterios del evento
    participantes_calificados = Participantes.objects.filter(
        calificacion__cal_criterio_fk__cri_evento_fk=evento_id
    ).distinct()

    return render(request, 'app_admin/ver_calificaciones.html', {
        'evento': evento,
        'participantes': participantes_calificados
    })

def ver_calificaciones_participante(request, evento_id, participante_id):
    """Ver calificaciones específicas de un participante"""
    evento = get_object_or_404(Evento, pk=evento_id)
    participante = get_object_or_404(Participantes, pk=participante_id)

    # Calificaciones de este participante para el evento seleccionado
    calificaciones = Calificacion.objects.filter(
        cal_criterio_fk__cri_evento_fk=evento_id,
        cal_participante_fk=participante_id
    ).select_related('cal_criterio_fk', 'cal_evaluador_fk').values(
        'cal_criterio_fk__cri_descripcion',
        'cal_evaluador_fk__eva_nombre',
        'cal_valor'
    )

    return render(request, 'app_admin/calificaciones_participante.html', {
        'evento': evento,
        'participante': participante,
        'calificaciones': calificaciones
    })





def descargar_ranking(request, evento_id):
    """Descargar ranking en formato CSV"""
    evento = get_object_or_404(Evento, pk=evento_id)

    # Buscar participantes de este evento
    participantes_evento = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=evento_id
    ).select_related('par_eve_participante_fk')
    
    data = []
    for pe in participantes_evento:
        participante = pe.par_eve_participante_fk
        # Calificaciones de ese participante
        calificaciones = Calificacion.objects.filter(cal_participante_fk=participante.par_id)
        puntaje_total = sum(c.cal_valor for c in calificaciones)

        data.append({
            'participante_id': participante.par_id,
            'participante_nombre': participante.par_nombre,
            'puntaje_total': puntaje_total
        })

    # Ordenar por puntaje total descendente
    data.sort(key=lambda x: x['puntaje_total'], reverse=True)

    # Crear el CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ranking_evento_{evento_id}.csv"'

    writer = csv.writer(response)
    
    # Encabezados del CSV
    headers = ["Posición", "Participante", "Puntaje Total"]
    writer.writerow(headers)

    # Escribir filas de datos
    for posicion, participante in enumerate(data, start=1):
        participante_nombre = participante.get('participante_nombre', 'Nombre Desconocido')
        participante_id = participante.get('participante_id', 'ID Desconocido')
        puntaje_total = participante.get('puntaje_total', 0)

        fila = [
            posicion,
            f"{participante_nombre} ({participante_id})",
            "{:.2f}".format(puntaje_total)
        ]
        writer.writerow(fila)

    return response
