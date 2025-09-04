from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q, Count
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import mark_safe
from django.db import transaction
from app_eventos.models import Evento
from app_participantes.models import Participantes, ParticipantesEventos
from app_registros.models import Asistentes, AsistentesEventos
from app_evaluadores.models import Criterio, Instrumento, Calificacion, Evaluador, EvaluadorEventos
from django.utils.timezone import now
from app_admin.models import AdministradorEvento, PlantillaCertificado
import logging
logger = logging.getLogger(__name__)

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

from django.contrib.auth.decorators import login_required

from django.http import HttpResponseForbidden
from app_super_admin.models import Categoria
from app_eventos.models import EventoCategoria


@login_required
def ventana(request):
    print("➡️ Entró a la vista ventana con usuario:", request.user)

    if request.user.rol != 'ADMINISTRADOR':
        print("❌ Rol inválido:", request.user.rol)
        return HttpResponseForbidden("⛔ Acceso denegado. No tienes permiso.")

    try:
        admin = AdministradorEvento.objects.get(usuario=request.user)
        print("✅ Admin encontrado:", admin)
        if not admin.aprobado:
            print("❌ Admin no aprobado")
            return HttpResponseForbidden("⛔ Tu cuenta aún no ha sido aprobada por el superadministrador.")
    except AdministradorEvento.DoesNotExist:
        print("❌ No existe AdministradorEvento para el usuario")
        return HttpResponseForbidden("⛔ No estás registrado como administrador de eventos.")

    eventos = Evento.objects.filter(adm_id=admin)
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
        
        
    categorias = Categoria.objects.all()
    if categorias.exists():
        for categoria in categorias:
            try:
                EventoCategoria.objects.create(evento=evento, categoria=categoria)
                print(f"✅ Evento {evento.pk} asociado a categoría {categoria.id}")
            except Exception as e:
                print(f"❌ Error al asociar categoría: {e}")

    print(f"📊 Eventos encontrados: {eventos.count()}")

    return render(request, 'app_admin/administrador_evento.html', {'eventos': eventos, 'estadisticas': estadisticas, 'categorias': categorias})





def gestionar_inscripciones(request, eve_id):
    """Gestionar inscripciones de participantes"""
    evento = get_object_or_404(Evento, pk=eve_id)
    
    # Query similar to the Flask SQLAlchemy join
    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=eve_id
    ).select_related('par_eve_participante_fk__usuario')
    plantillas = PlantillaCertificado.objects.all()

    
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
        'participantes': participantes,
        'plantillas': plantillas
    })


def gestionar_inscripcion_asis(request, eve_id):
    """Gestionar inscripciones de asistentes"""
    evento = get_object_or_404(Evento, pk=eve_id)

    asistentes_eventos = AsistentesEventos.objects.filter(
    asi_eve_evento_fk=evento
).select_related("asi_eve_asistente_fk__usuario")
    plantillas = PlantillaCertificado.objects.all()


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
        'asistentes': asistentes,
        'plantillas': plantillas
    })
    
def gestionar_evaluadores(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    evaluadores_eventos = EvaluadorEventos.objects.filter(
        eva_eve_evento_fk=evento_id
    ).select_related('eva_eve_evaluador_fk')
    
    plantillas = PlantillaCertificado.objects.all()


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
        'evaluadores': evaluadores,
        'plantillas': plantillas
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

from twilio.rest import Client
from django.conf import settings

def enviar_sms(destinatario, mensaje):
   
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=destinatario
        )
        return message.sid  # Devuelve el SID como confirmación
    except Exception as e:
        # Puedes loguearlo o manejarlo como desees
        print(f"Error al enviar SMS: {e}")
        return None


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
                
            print("Participante:", participante.id, "Evento:", evento.eve_id, "Estado:", nuevo_estado)



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
                
                
                telefono = usuario.telefono.strip()
                if not telefono.startswith('+'):
                    telefono = '+57' + telefono.lstrip('0')  # Colombia por defecto
                mensaje_sms = (
                    f"Hola {usuario.first_name}, fuiste aceptado como Participante en {evento.eve_nombre}.\n"
                    f"Usuario: {usuario.email}\nContraseña: {nueva_password}"
                )
                enviar_sms(telefono, mensaje_sms)
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
                
                telefono = usuario.telefono.strip()
                if not telefono.startswith('+'):
                    telefono = '+57' + telefono.lstrip('0') (
                    f"Hola {usuario.first_name}, fuiste aceptado como Participante en {evento.eve_nombre}.\n"
                    f"Usuario: {usuario.email}\nContraseña: {nueva_password}\nPor favor cambia tu contraseña después de iniciar sesión."
                )
                enviar_sms(telefono, mensaje_sms)
                
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
                
                telefono = usuario.telefono.strip()
                if not telefono.startswith('+'):
                    telefono = '+57' + telefono.lstrip('0')  
                mensaje_sms = (
                    f"Hola {usuario.first_name}, fuiste aceptado como Participante en {evento.eve_nombre}.\n"
                    f"Usuario: {usuario.email}\nContraseña: {nueva_password}"
                )
                enviar_sms(telefono, mensaje_sms)
            else:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [correo])
        else:
            messages.error(request, "Rol no válido.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        messages.success(request, "Estado actualizado correctamente y correo enviado.")
        return redirect('admin_evento:ventana')

    except Exception as e:
        messages.error(request, f"Error al actualizar el estado: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))


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


from django.db.models import F
import logging
logger = logging.getLogger(__name__)


@login_required
def ver_ranking_admin(request, evento_id):
    """Ver ranking de participantes en un evento"""
    logger.info(f"⚠️ ENTRANDO a ver_ranking_admin con evento_id={evento_id}")

    evento = get_object_or_404(Evento, pk=evento_id)
    logger.info(f"✅ Evento encontrado: {evento.eve_nombre} (ID: {evento.eve_id})")

    try:
        # Obtener ranking usando anotaciones con calificaciones y pesos
        ranking_query = Participantes.objects.filter(
            calificacion__cal_criterio_fk__cri_evento_fk=evento_id
        ).annotate(
            puntaje_total=Sum(
                F('calificacion__cal_valor') * F('calificacion__cal_criterio_fk__cri_peso')
            )
        ).values(
            'id', 'usuario__first_name', 'usuario__last_name', 'puntaje_total'
        ).order_by('-puntaje_total')

        logger.info(f"🔍 Participantes encontrados en ranking: {ranking_query.count()}")
    except Exception as e:
        logger.error(f"❌ Error al calcular el ranking: {e}")
        messages.error(request, "Ocurrió un error al generar el ranking.")
        return redirect('admin_evento:panel_eventos')  # o redirección más adecuada

    ranking = []
    for item in ranking_query:
        nombre = f"{item['usuario__first_name']} {item['usuario__last_name']}"
        puntaje = item['puntaje_total'] or 0
        logger.debug(f"🏅 {nombre} → Puntaje: {puntaje}")
        ranking.append({
            'participante_id': item['id'],
            'participante_nombre': nombre,
            'puntaje_total': puntaje
        })

    logger.warning(f"🧾 Total en ranking final: {len(ranking)} participantes")

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

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas



from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm



from django.contrib.auth.models import User
from app_admin.forms import PlantillaCertificadoForm


@login_required
def crear_plantilla_certificado(request):
    form = PlantillaCertificadoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✅ Plantilla creada exitosamente.")
        return redirect("admin_evento:listar_plantillas_certificado")
    return render(request, "app_admin/crear_plantilla.html", {"form": form})

@login_required
def listar_plantillas_certificado(request):
    print("🌟 Entrando a la vista listar_plantillas_certificado")
    plantillas = PlantillaCertificado.objects.all()
    print(f"🔍 Se encontraron {plantillas.count()} plantillas")
    return render(request, 'app_admin/listar_plantillas.html', {'plantillas': plantillas})

from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

def generar_certificado_pdf(usuario, evento, tipo, plantilla):
    buffer = BytesIO()
    width, height = landscape(A4)
    p = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ----- Fondo -----
    p.setFillColor(HexColor(plantilla.color_fondo))
    p.rect(0, 0, width, height, stroke=0, fill=1)

    # ----- Marco externo -----
    p.setStrokeColor(HexColor(plantilla.color_borde))
    p.setLineWidth(plantilla.borde_grosor)
    p.rect(plantilla.borde_margen, plantilla.borde_margen,
           width - 2*plantilla.borde_margen, height - 2*plantilla.borde_margen)

   
    # ----- Título principal -----
    p.setFont("Helvetica-Bold", 32)
    p.setFillColor(HexColor(plantilla.color_titulo))
    p.drawCentredString(width / 2, height - 5*cm, plantilla.titulo)

    # ----- Subtítulo elegante -----
    p.setFont("Helvetica", 18)
    p.setFillColor(black)
    p.drawCentredString(width / 2, height - 6.2*cm, plantilla.subtitulo)

    # Línea decorativa debajo del subtítulo
    p.setStrokeColor(HexColor(plantilla.color_borde))
    p.setLineWidth(1.2)
    p.line(width/4, height - 6.6*cm, width*3/4, height - 6.6*cm)

    # ----- Nombre del usuario destacado -----
    full_name = f"{usuario.first_name} {usuario.last_name}".upper()
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(HexColor(plantilla.color_nombre))
    p.drawCentredString(width / 2, height - 9*cm, full_name)

    # Línea fina debajo del nombre
    p.setStrokeColor(HexColor(plantilla.color_nombre))
    p.setLineWidth(0.8)
    p.line(width/4, height - 9.3*cm, width*3/4, height - 9.3*cm)

    # ----- Tipo de participación elegante -----
    tipo_label = tipo.upper()
    p.setFont("Helvetica-BoldOblique", 16)
    p.setFillColor(HexColor(plantilla.color_titulo))
    p.drawCentredString(width / 2, height - 11*cm, f"Participación: {tipo_label}")

    # ----- Evento elegante -----
    evento_nombre = evento.eve_nombre.upper()
    p.setFont("Helvetica-BoldOblique", 16)
    p.setFillColor(HexColor(plantilla.color_titulo))
    p.drawCentredString(width / 2, height - 12*cm, f"Evento: {evento_nombre}")

    # ----- Logo a la izquierda -----
    if plantilla.logo:
        try:
            logo = ImageReader(plantilla.logo.path)
            p.drawImage(logo, x=2*cm, y=height - 6*cm, width=4*cm, height=4*cm, mask="auto")
        except:
            pass

    # ----- Sello a la derecha -----
    if plantilla.sello:
        try:
            sello = ImageReader(plantilla.sello.path)
            p.drawImage(sello, x=width - 6*cm, y=2*cm, width=4*cm, height=4*cm, mask="auto")
        except:
            pass

    # ----- Firma elegante -----
    p.setFont("Helvetica", 12)
    p.setFillColor(black)
    p.drawString(plantilla.borde_margen + 1*cm, 3*cm, "_________________________")
    p.drawString(plantilla.borde_margen + 1*cm, 2*cm, plantilla.texto_firma)

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf




def previsualizar_certificado(request, plantilla_id):
    plantilla = get_object_or_404(PlantillaCertificado, pk=plantilla_id)
    usuario = request.user if request.user.is_authenticated else User.objects.first()
    evento = Evento.objects.first()  # Cambia por el evento que quieras
    tipo = "asistente"  # Por ejemplo: 'asistente', 'evaluador', 'participante'

    pdf = generar_certificado_pdf(usuario, evento, tipo, plantilla)
    return HttpResponse(pdf, content_type="application/pdf")


@login_required
def editar_plantilla_certificado(request, plantilla_id):
    plantilla = get_object_or_404(PlantillaCertificado, id=plantilla_id)
    form = PlantillaCertificadoForm(request.POST or None, request.FILES or None, instance=plantilla)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✏️ Plantilla actualizada correctamente.")
        return redirect("admin_evento:listar_plantillas_certificado")
    return render(request, "app_admin/editar_plantilla.html", {"form": form, "plantilla": plantilla})
@login_required
def eliminar_plantilla(request, plantilla_id):
    plantilla = get_object_or_404(PlantillaCertificado, id=plantilla_id)
    plantilla.delete()
    messages.success(request, "Plantilla eliminada correctamente.")
    return redirect('admin_evento:listar_plantillas_certificado')


@login_required
def seleccionar_plantilla_envio(request, evento_id, rol):
    evento = get_object_or_404(Evento, pk=evento_id)
    plantillas = PlantillaCertificado.objects.all()

    if request.method == 'POST':
        plantilla_id = request.POST.get('plantilla_id')
        if not plantilla_id:
            messages.error(request, "Selecciona una plantilla.")
            return redirect(request.path)

        plantilla = get_object_or_404(PlantillaCertificado, pk=plantilla_id)

        return redirect(f'/admin_evento/evento/{evento_id}/enviar-certificados/{rol}/?plantilla_id={plantilla.id}')

    return render(request, 'admin_evento/seleccionar_plantilla.html', {
        'evento': evento,
        'rol': rol,
        'plantillas': plantillas,
    })


from django.contrib.auth.models import User

def enviar_certificado(usuario, evento, tipo, archivo_pdf):
    """Envía el certificado por correo electrónico."""
    asunto = f'🎓 Certificado de {tipo.capitalize()} - {evento.eve_nombre}'

    mensaje = f"""
    Hola {usuario.first_name},

    Adjuntamos tu certificado como {tipo} del evento "{evento.eve_nombre}".

    ¡Gracias por participar!
    """

    try:
        logger.debug(f"[EMAIL] Preparando envío de certificado {tipo} a {usuario.email}")

        email = EmailMessage(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            [usuario.email]
        )

        # Adjuntar el archivo PDF
        email.attach(f"certificado_{tipo}.pdf", archivo_pdf, "application/pdf")

        email.send()
        logger.debug(f"[EMAIL] Certificado enviado correctamente a {usuario.email}")
    except Exception as e:
        logger.error(f"[EMAIL] Error al enviar a {usuario.email}: {e}")

from django.http import HttpResponseNotAllowed

#########################

def enviar_certificados_asistentes(request, evento_id):
    logger.info(f"[MASIVO] Ingresando a enviar_certificados_asistentes con evento_id={evento_id}")

    plantilla_id = request.POST.get('plantilla_id')
    if not plantilla_id:
        messages.error(request, "❌ Debes seleccionar una plantilla.")
        return redirect('admin_evento:gestionar_inscripcion_asis', eve_id=evento_id)

    plantilla = get_object_or_404(PlantillaCertificado, pk=plantilla_id)

    evento = get_object_or_404(Evento, pk=evento_id)
    logger.debug(f"[MASIVO] Evento encontrado: {evento.eve_nombre}")

    try:
        relaciones = AsistentesEventos.objects.filter(asi_eve_evento_fk=evento)
        logger.debug(f"[MASIVO] Total relaciones encontradas: {relaciones.count()}")
    except Exception as e:
        logger.error(f"[MASIVO] Error al obtener relaciones: {e}")
        messages.error(request, "❌ Error al obtener la lista de asistentes.")
        return redirect('admin_evento:gestionar_inscripcion_asis', eve_id=evento_id)

    enviados = 0
    for rel in relaciones:
        usuario = rel.asi_eve_asistente_fk.usuario
        logger.debug(f"[MASIVO] Enviando certificado a: {usuario.email}")
        try:
            pdf = generar_certificado_pdf(usuario, evento, 'asistente', plantilla=plantilla)
            enviar_certificado(usuario, evento, 'asistente', pdf)
            enviados += 1
        except Exception as e:
            logger.error(f"[MASIVO] Error al generar o enviar certificado para {usuario.email}: {e}")

    logger.info(f"[MASIVO] Total enviados: {enviados}")
    messages.success(request, f"🎉 Certificados enviados a {enviados} asistentes.")
    return redirect('admin_evento:gestionar_inscripcion_asis', eve_id=evento_id)

@login_required
def enviar_certificado_asistente_individual(request, evento_id, usuario_id):
    logger.debug(f"[INDIVIDUAL] Ingresando con evento_id={evento_id}, usuario_id={usuario_id}")
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    plantilla_id = request.POST.get('plantilla_id')
    if not plantilla_id:
        messages.error(request, "Debes seleccionar una plantilla.")
        return redirect('admin_evento:gestionar_inscripcion_asis', eve_id=evento_id)

    plantilla = get_object_or_404(PlantillaCertificado, pk=plantilla_id)
    evento = get_object_or_404(Evento, pk=evento_id)
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    try:
        logger.debug(f"[INDIVIDUAL] Generando PDF para {usuario.email}")
        pdf = generar_certificado_pdf(usuario, evento, 'asistente', plantilla=plantilla)
        
    except Exception as e:
        logger.debug(f"[INDIVIDUAL] Enviando certificado a {usuario.email}")
        enviar_certificado(usuario, evento, 'asistente', pdf)

    messages.success(request, f"📨 Certificado enviado a {usuario.first_name} {usuario.last_name}.")
    return redirect(f"{reverse('admin_evento:gestionar_inscripcion_asis', args=[evento_id])}?exito=1")


#######################33


@login_required
def enviar_certificados_participantes(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    plantilla_id = request.POST.get('plantilla_id')

    if not plantilla_id:
        messages.error(request, "❌ Debes seleccionar una plantilla para enviar los certificados.")
        return redirect('admin_evento:gestionar_inscripciones', eve_id=evento_id)

    try:
        plantilla = PlantillaCertificado.objects.get(pk=plantilla_id)
    except PlantillaCertificado.DoesNotExist:
        messages.error(request, "❌ La plantilla seleccionada no existe.")
        return redirect('admin_evento:gestionar_inscripciones', eve_id=evento_id)

    try:
        relaciones = ParticipantesEventos.objects.filter(
            par_eve_evento_fk=evento
        )
    except Exception as e:
        logger.error(f"[MASIVO] Error al obtener relaciones: {e}")
        messages.error(request, "❌ Error al obtener la lista de participantes.")
        return redirect('admin_evento:gestionar_inscripciones', eve_id=evento_id)

    enviados = 0
    for rel in relaciones:
        usuario = rel.par_eve_participante_fk.usuario
        logger.debug(f"[MASIVO] Enviando certificado a: {usuario.email}")
        pdf = generar_certificado_pdf(usuario, evento, 'participante', plantilla=plantilla)
        enviar_certificado(usuario, evento, 'participante', pdf)
        enviados += 1

    logger.info(f"[MASIVO] Total certificados enviados a participantes: {enviados}")
    messages.success(request, f"🎉 Certificados enviados a {enviados} participantes.")
    return redirect('admin_evento:gestionar_inscripciones', eve_id=evento_id)

@login_required
def enviar_certificado_participante_individual(request, evento_id, usuario_id):
    logger.debug(f"[INDIVIDUAL] Ingresando con evento_id={evento_id}, usuario_id={usuario_id}")
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    plantilla_id = request.POST.get('plantilla_id')
    if not plantilla_id:
        messages.error(request, "Debes seleccionar una plantilla.")
        return redirect('admin_evento:gestionar_inscripcion_asis', eve_id=evento_id)

    plantilla = get_object_or_404(PlantillaCertificado, pk=plantilla_id)
    evento = get_object_or_404(Evento, pk=evento_id)
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    try:
        logger.debug(f"[INDIVIDUAL] Generando PDF para {usuario.email}")
        pdf = generar_certificado_pdf(usuario, evento, 'participante', plantilla)
        
    except Exception as e:
        logger.debug(f"[INDIVIDUAL] Enviando PDF para {usuario.email}")     
        enviar_certificado(usuario, evento, 'participante', pdf)

    messages.success(request, f"📨 Certificado enviado a {usuario.first_name} {usuario.last_name}.")
    return redirect(f"{reverse('admin_evento:gestionar_inscripciones', args=[evento_id])}?exito=1")

##########################################

@login_required
def enviar_certificados_evaluadores(request, evento_id):
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('admin_evento:gestionar_evaluadores', eve_id=evento_id)

    evento = get_object_or_404(Evento, pk=evento_id)
    logger.debug(f"[MASIVO] Evento encontrado: {evento.eve_nombre}")

    plantilla_id = request.POST.get('plantilla_id')
    if not plantilla_id:
        messages.error(request, "❌ Debes seleccionar una plantilla para enviar los certificados.")
        return redirect('admin_evento:gestionar_evaluadores', eve_id=evento_id)

    try:
        plantilla = PlantillaCertificado.objects.get(pk=plantilla_id)
    except PlantillaCertificado.DoesNotExist:
        messages.error(request, "❌ La plantilla seleccionada no existe.")
        return redirect('admin_evento:gestionar_evaluadores', eve_id=evento_id)

    try:
        relaciones = EvaluadorEventos.objects.filter(
            eva_eve_evento_fk=evento,
            eva_eve_evaluador_fk__usuario__rol='EVALUADOR'
        )
        logger.debug(f"[MASIVO] Total relaciones encontradas: {relaciones.count()}")
    except Exception as e:
        logger.error(f"[MASIVO] Error al obtener relaciones: {e}")
        messages.error(request, "❌ Error al obtener la lista de Evaluadores.")
        return redirect('admin_evento:gestionar_evaluadores', eve_id=evento_id)

    enviados = 0
    for rel in relaciones:
        usuario = rel.eva_eve_evaluador_fk.usuario
        logger.debug(f"[MASIVO] Enviando certificado a: {usuario.email}")
        pdf = generar_certificado_pdf(usuario, evento, 'evaluador', plantilla=plantilla)
        enviar_certificado(usuario, evento, 'evaluador', pdf)
        enviados += 1

    logger.info(f"[MASIVO] Total enviados: {enviados}")
    messages.success(request, f"🎉 Certificados enviados a {enviados} evaluadores.")
    return redirect(f"{reverse('admin_evento:gestionar_evaluadores', args=[evento_id])}?exito=1")

 
@login_required
def enviar_certificado_evaluador_individual(request, evento_id, usuario_id):
    logger.debug(f"[INDIVIDUAL] Ingresando con evento_id={evento_id}, usuario_id={usuario_id}")
    
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    plantilla_id = request.POST.get('plantilla_id')
    if not plantilla_id:
        messages.error(request, "Debes seleccionar una plantilla.")
        return redirect('admin_evento:gestionar_inscripcion_asis', eve_id=evento_id)

    plantilla = get_object_or_404(PlantillaCertificado, pk=plantilla_id)
    evento = get_object_or_404(Evento, pk=evento_id)
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    try:
        pdf = generar_certificado_pdf(usuario, evento, 'evaluador', plantilla)
        enviar_certificado(usuario, evento, 'evaluador', pdf)
        messages.success(request, f"📨 Certificado enviado a {usuario.first_name} {usuario.last_name}.")

    except Exception as e:
        logger.error(f"Error al enviar certificado: {e}")
        messages.error(request, "Ocurrió un error al enviar el certificado.")

    return redirect(f"{reverse('admin_evento:gestionar_evaluadores', args=[evento_id])}?exito=1")

########## MANEJO DE NOTIFICACIONES PARA CADA ROL 


@login_required
def notificar_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == 'POST':
        mensaje_adicional = request.POST.get('mensaje_adicional', '').strip()
        destinatarios = request.POST.getlist('destinatarios') 

        total = 0
        enviados_a = set()

        encabezado = (
            f"Hola,\n\n"
            f"Te enviamos información importante sobre el evento:\n\n"
            f"📌 Nombre: {evento.eve_nombre}\n"
        )

        if hasattr(evento, 'eve_fecha') and evento.eve_fecha:
            encabezado += f"📅 Fecha: {evento.eve_fecha.strftime('%d/%m/%Y')}\n"
        if hasattr(evento, 'eve_hora') and evento.eve_hora:
            encabezado += f"⏰ Hora: {evento.eve_hora.strftime('%I:%M %p')}\n"

        encabezado += "\n"
        mensaje_completo = encabezado + mensaje_adicional + "\n\nSaludos,\nEquipo organizador"

        
        modelos = {
            'participantes': (ParticipantesEventos, 'par_eve_participante_fk'),
            'evaluadores': (EvaluadorEventos, 'eva_eve_evaluador_fk'),
            'asistentes': (AsistentesEventos, 'asi_eve_asistente_fk'),
        }

        for rol in destinatarios:
            modelo, attr = modelos[rol]
            relaciones = modelo.objects.filter(**{f'{attr[:3]}_eve_evento_fk': evento})
            for rel in relaciones:
                usuario = getattr(rel, attr).usuario
                if usuario.email and usuario.email not in enviados_a:
                    send_mail(
                        subject=f"📢 Información del evento {evento.eve_nombre}",
                        message=mensaje_completo,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[usuario.email],
                        fail_silently=False,
                    )
                    enviados_a.add(usuario.email)
                    total += 1

        messages.success(request, f"📨 Se enviaron {total} notificaciones.")
        return redirect('admin_evento:ventana')

    return render(request, 'app_admin/enviar_notificaciones.html', {'evento': evento})