from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, F, Q
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
import os

from .utils import save_file

from app_eventos.models import Evento
from app_participantes.models import Participantes, ParticipantesEventos
from app_evaluadores.models import Criterio, Instrumento, Calificacion, Evaluador, EvaluadorEventos, InformacionTecnica
from app_usuarios.models import Usuario


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail

from django.http import HttpResponseForbidden


def enviar_correo(destinatario, asunto, mensaje):
    email_desde = settings.EMAIL_HOST_USER
    destinatarios = [destinatario]
    send_mail(asunto, mensaje, email_desde, destinatarios, fail_silently=False)
    
    
@login_required
def perfil_evaluador(request):
    usuario = request.user

    if usuario.rol != 'EVALUADOR':
        messages.error(request, "No tienes permiso para ver este perfil.")
        return redirect('main:lista_eventos')

    evaluador = get_object_or_404(Evaluador, usuario=usuario)

    return render(request, 'app_evaluadores/perfil_evaluador.html', {
        'usuario': usuario,
        'evaluador': evaluador,
    })    

@login_required
def seleccionar_evento_evaluador(request):
    evaluador = Evaluador.objects.get(usuario=request.user)
    eventos_asignados = EvaluadorEventos.objects.filter(eva_eve_evaluador_fk=evaluador)

    return render(request, "evaluadores/seleccionar_evento.html", {
        "eventos_asignados": eventos_asignados
    })
@login_required
# --- Panel evaluador ---
def panel_evaluador(request, eva_id, evento_id):
    evaluador = get_object_or_404(Evaluador, pk=eva_id)
    evento = get_object_or_404(Evento, pk=evento_id)
    
    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=evento,
        par_estado='ACEPTADO'
    )
    participantes = [pe.par_eve_participante_fk for pe in participantes_eventos]

    context = {
        'evaluador': evaluador,
        'evento': evento,
        'participantes': participantes
    }
    return render(request, 'app_evaluadores/panel_evaluador.html', context)


# --- Seleccionar evento (requiere login manual, sin auth) ---
@login_required
def seleccionar_evento(request):
    usuario = request.user
    
    try:
        evaluador = Evaluador.objects.get(usuario=usuario)
    except Evaluador.DoesNotExist:
        return render(request, "evaluadores/seleccionar_evento.html", {
            'eventos': [],
            'evaluador': None
        })

    eventos = Evento.objects.filter(evaluadores=evaluador, eve_estado="ACTIVO").distinct()

    return render(request, "app_evaluadores/seleccionar_evento.html", {
        'eventos': eventos,
        'evaluador': evaluador
    })
@login_required
# --- Gestionar criterios ---
@require_http_methods(["GET", "POST"])
def gestionar_criterios(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    criterios = Criterio.objects.filter(cri_evento_fk=evento)
    instrumento = Instrumento.objects.filter(inst_evento_fk=evento).first()

    if request.method == 'POST':
        accion = request.POST.get('accion')
        peso_str = request.POST.get('peso')

        try:
            peso = float(peso_str) if peso_str else 0
        except ValueError:
            messages.error(request, 'El peso ingresado no es válido.')
            return redirect(reverse('admin:gestionar_criterios_admin', args=[evento_id]))

        if accion == 'crear':
            descripcion = request.POST.get('descripcion')
            suma_actual = criterios.aggregate(suma=Sum('cri_peso'))['suma'] or 0
            if suma_actual + peso > 100:
                messages.error(request, f'Error: La suma de los porcentajes no puede superar el 100% (actual: {suma_actual}%, intento agregar: {peso}%).')
                messages.error(request, f'Por favor, ajuste el peso del nuevo criterio, queda por agregar un {100 - suma_actual}%.')
                return redirect(reverse('admin:gestionar_criterios_admin', args=[evento_id]))
            else:
                Criterio.objects.create(
                    cri_descripcion=descripcion,
                    cri_peso=peso,
                    cri_evento_fk=evento
                )
                messages.success(request, 'Criterio creado exitosamente.')

        elif accion == 'editar':
            criterio_id = request.POST.get('criterio_id')
            criterio = get_object_or_404(Criterio, pk=criterio_id)
            suma_sin_este = criterios.exclude(pk=criterio.pk).aggregate(suma=Sum('cri_peso'))['suma'] or 0

            if suma_sin_este + peso > 100:
                messages.error(request, f'Error: La suma de los porcentajes no puede superar el 100% (actual sin este: {suma_sin_este}%, intento editar a: {peso}%).')
                return redirect(reverse('admin:gestionar_criterios_admin', args=[evento_id]))
            else:
                criterio.cri_descripcion = request.POST.get('descripcion')
                criterio.cri_peso = peso
                criterio.save()
                messages.success(request, 'Criterio actualizado exitosamente.')

        elif accion == 'eliminar':
            criterio_id = request.POST.get('criterio_id')
            criterio = get_object_or_404(Criterio, pk=criterio_id)
            calificaciones_vinculadas = Calificacion.objects.filter(cal_criterio_fk=criterio).count()
            if calificaciones_vinculadas > 0:
                messages.error(request, f'No se puede eliminar el criterio "{criterio.cri_descripcion}" porque tiene {calificaciones_vinculadas} calificación(es) asociada(s).')
            else:
                criterio.delete()
                messages.success(request, 'Criterio eliminado exitosamente.')

        return redirect(reverse('admin_evento:gestionar_criterios_admin', args=[evento_id]))

    total_peso = criterios.aggregate(total=Sum('cri_peso'))['total'] or 0

    return render(request, 'app_evaluadores/criterios.html', {
        'criterios': criterios,
        'instrumento': instrumento,
        'evento_id': evento_id,
        'total_peso': round(total_peso, 2),
        'evento': evento
    })


@login_required
# --- Cargar instrumento ---
@require_http_methods(["GET", "POST"])
def cargar_instrumento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    instrumento = Instrumento.objects.filter(inst_evento_fk=evento).first()

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')

        if instrumento:
            instrumento.inst_tipo = tipo
            instrumento.inst_descripcion = descripcion
            instrumento.save()
            messages.success(request, 'Instrumento actualizado exitosamente.')
        else:
            Instrumento.objects.create(
                inst_tipo=tipo,
                inst_descripcion=descripcion,
                inst_evento_fk=evento
            )
            messages.success(request, 'Instrumento cargado exitosamente.')

        return redirect(reverse('evaluadores:cargar_instrumento', args=[evento_id]))

    return render(request, 'app_evaluadores/cargar_instrumento.html', {
        'instrumento': instrumento,
        'evento_id': evento_id
    })

@login_required
@require_http_methods(["GET", "POST"])
def cargar_informacion_tecnica(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    info_tecnica = InformacionTecnica.objects.filter(inf_evento_fk=evento).first()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        if info_tecnica:
            info_tecnica.inf_nombre = nombre
            info_tecnica.inf_descripcion = descripcion
            info_tecnica.save()
            messages.success(request, 'Información técnica actualizada exitosamente.')
        else:
            InformacionTecnica.objects.create(
                inf_nombre=nombre,
                inf_descripcion=descripcion,
                inf_evento_fk=evento
            )
            messages.success(request, 'Información técnica cargada exitosamente.')

        return redirect(reverse('evaluadores:cargar_informacion_tecnica', args=[evento_id]))

    return render(request, 'app_evaluadores/cargar_informacion.html', {
        'informacion_tecnica': info_tecnica,
        'evento_id': evento_id
    })





# --- Lista participantes ---
@login_required
def lista_participantes(request, evento_id):
    try:
        evaluador = request.user.evaluador  # gracias a OneToOneField
    except Evaluador.DoesNotExist:
        return HttpResponseForbidden("No tienes permisos para acceder a esta vista.")

    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=evento_id,
        par_estado='ACEPTADO'
    ).select_related('par_eve_participante_fk')

    participantes = [pe.par_eve_participante_fk for pe in participantes_eventos]

    return render(request, 'app_evaluadores/lista_participantes.html', {
        'evento_id': evento_id,
        'participantes': participantes,
        'evaluador_id': evaluador.id  # <-- para que esté disponible en el template
    })

@login_required
# --- Calificar participante ---
@require_http_methods(["GET", "POST"])
def calificar_participante(request, eva_id, evento_id, par_id):
    evaluador = get_object_or_404(Evaluador, pk=eva_id)
    evento = get_object_or_404(Evento, pk=evento_id)
    participante = get_object_or_404(Participantes, pk=par_id)

    criterios = Criterio.objects.filter(cri_evento_fk=evento)

    if request.method == 'POST':
        for criterio in criterios:
            field_name = f'criterio_{criterio.pk}'
            if field_name in request.POST:
                try:
                    valor = int(request.POST[field_name])
                except ValueError:
                    messages.error(request, f"El valor para el criterio {criterio.cri_descripcion} debe ser numérico.")
                    continue

                calificacion, created = Calificacion.objects.get_or_create(
                    cal_evaluador_fk=evaluador,
                    cal_criterio_fk=criterio,
                    cal_participante_fk=participante,
                    defaults={'cal_valor': valor}
                )
                if not created:
                    calificacion.cal_valor = valor
                    calificacion.save()

        messages.success(request, "Calificaciones guardadas correctamente.")
        return redirect(reverse('evaluadores:calificar_participante', args=[evaluador.pk, evento.pk, participante.pk]))

    # Obtener calificaciones existentes
    calificaciones = Calificacion.objects.filter(
        cal_evaluador_fk=evaluador,
        cal_participante_fk=participante
    )
    cal_dict = {cal.cal_criterio_fk_id: cal.cal_valor for cal in calificaciones}

    # Armar lista con criterios y valores para pasar al template
    criterios_con_valor = []
    for criterio in criterios:
        valor = cal_dict.get(criterio.pk)
        criterios_con_valor.append({
            'criterio': criterio,
            'valor': valor,
        })

    return render(request, 'app_evaluadores/calificar.html', {
        'evaluador': evaluador,
        'evento': evento,
        'participante': participante,
        'criterios_con_valor': criterios_con_valor,
    })

from django.db.models import F, Sum, FloatField, ExpressionWrapper

@login_required
# --- Ver ranking ---
def ver_ranking(request, evento_id):
    evaluador = get_object_or_404(Evaluador, usuario=request.user)
    evento = get_object_or_404(Evento, pk=evento_id)

    ranking = (
        Participantes.objects.filter(
            calificacion__cal_criterio_fk__cri_evento_fk=evento
        )
        .annotate(
            puntaje_total=Sum(
                ExpressionWrapper(
                    F('calificacion__cal_valor') * F('calificacion__cal_criterio_fk__cri_peso') / 100,
                    output_field=FloatField()
                )
            )
        )
        .select_related('usuario')  # Para acceder a nombres fácilmente en la plantilla
        .order_by('-puntaje_total')
        .distinct()
    )

    return render(request, 'app_evaluadores/ranking.html', {
        'evaluador': evaluador,
        'evento': evento,
        'ranking': ranking
    })


# --- Login evaluador ---



# --- Logout evaluador ---
def logout_evaluador(request):
    request.session.pop('evaluador_id', None)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('main:login_view|')

@login_required
# --- Ver calificaciones evento ---
def ver_calificaciones_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    participantes_calificados = Participantes.objects.filter(
        calificacion__cal_criterio_fk__cri_evento_fk=evento
    ).distinct()

    return render(request, 'app_evaluadores/ver_calificaciones.html', {
        'evento': evento,
        'participantes': participantes_calificados
    })

@login_required
# --- Ver calificaciones participante ---
def ver_calificaciones_participante(request, evento_id, participante_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    participante = get_object_or_404(Participantes, pk=participante_id)

    calificaciones = Calificacion.objects.filter(
        cal_criterio_fk__cri_evento_fk=evento,
        cal_participante_fk=participante
    ).select_related(
        'cal_criterio_fk', 'cal_evaluador_fk__usuario'
    ) # Opcional: orden por nombre de criterio

    context = {
        'evento': evento,
        'participante': participante,
        'calificaciones': calificaciones
    }

    return render(request, 'app_evaluadores/calificaciones_participante.html', context)


######################## NUEVAS
@login_required

def verificar_evaluador(request):
    if request.method == 'POST':
        eva_id = request.POST.get('eva_id')
        if not eva_id:
            messages.warning(request, "Por favor, ingresa tu ID de evaluador.")
            return redirect('evaluadores:verificar_evaluador')

        try:
            evaluador = Evaluador.objects.get(pk=eva_id)
        except Evaluador.DoesNotExist:
            messages.error(request, "No se encontró un evaluador con este ID.")
            return redirect('evaluadores:verificar_evaluador')

        return redirect('evaluadores:modificar_evaluador', user_id=eva_id, evento_id=1)

    return render(request, 'app_evaluadores/verificar_evaluador.html')



def modificar_evaluador(request, user_id, evento_id):
    # Obtener el usuario y su evaluador relacionado
    usuario = get_object_or_404(Usuario, pk=user_id)
    evaluador = get_object_or_404(Evaluador, usuario=usuario)

    # Buscar la asignación al evento
    asignacion = EvaluadorEventos.objects.filter(
        eva_eve_evaluador_fk=evaluador,
        eva_eve_evento_fk_id=evento_id
    ).first()

    if not asignacion:
        messages.error(request, "No se encontró la asignación de este evaluador al evento.")
        return redirect('evaluadores:mi_info')

    if request.method == 'POST':
        # Captura y asignación manual de campos del usuario
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        if nombre:
            usuario.first_name = nombre
        if correo:
            usuario.email = correo
        if telefono:
            usuario.telefono = telefono

        # Procesar el archivo si se envió
        filename = None
        file = request.FILES.get('documento')
        if file:
            filename = save_file(
                file,
                upload_folder=settings.UPLOAD_FOLDER_PAGOS,
                allowed_extensions=settings.ALLOWED_EXTENSIONS_PAGOS
            )
            if filename:
                asignacion.eva_eve_documentos = filename
            else:
                messages.warning(request, "Archivo inválido o error al guardar.")

        usuario.save()
        asignacion.save()

        messages.success(request, "Datos del evaluador actualizados correctamente.")
        return redirect('evaluadores:mi_info')

    context = {
        'usuario': usuario,
        'evaluador': evaluador,
        'asignacion': asignacion,
        'evento_nombre': asignacion.eva_eve_evento_fk.eve_nombre,
    }
    return render(request, 'app_evaluadores/modificar_evaluador.html', context)


@login_required
def mi_info(request):
    usuario = request.user

    # Validar que el usuario tenga el rol adecuado
    if usuario.rol != 'EVALUADOR':
        messages.error(request, "No tienes permisos para ver esta información.")
        return redirect('main:lista_eventos')

    # Obtener el evaluador relacionado con el usuario actual
    try:
        evaluador = usuario.evaluador  # gracias al OneToOneField, puedes acceder directo
    except Evaluador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de Evaluador.")
        return redirect('main:lista_eventos')

    # Buscar eventos asignados
    asignaciones = EvaluadorEventos.objects.filter(
        eva_eve_evaluador_fk=evaluador,
        eva_eve_evento_fk__eve_estado="ACTIVO"
    ).select_related('eva_eve_evento_fk')

    eventos_asignados = []

    for asignacion in asignaciones:
        evento = asignacion.eva_eve_evento_fk

        eventos_asignados.append({
            'evento': {
                'eve_id': evento.eve_id,
                'eve_nombre': evento.eve_nombre,
                'eve_fecha_inicio': evento.eve_fecha_inicio,
                'eve_ciudad': evento.eve_ciudad,
            },
            'eva_estado': asignacion.eva_estado,
            'eva_eve_documentos': asignacion.eva_eve_documentos,
            'puntaje_total': 0,  # Por implementar
            'promedio': 0,
            'posicion': None,
            'instrumento': None,
            'criterios': [],
        })

    return render(request, "app_evaluadores/eva_informacion.html", {
        'titulo': "Mis Eventos Asignados",
        'evaluador': evaluador,
        'eventos_asignados': eventos_asignados,
    })

def cancelar_inscripcion(request, evento_id, user_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    correo = None

    try:
        # Obtener el usuario y luego el evaluador asociado
        usuario = get_object_or_404(Usuario, pk=user_id)
        evaluador = get_object_or_404(Evaluador, usuario=usuario)

        evaluador_evento = EvaluadorEventos.objects.get(
            eva_eve_evaluador_fk=evaluador,
            eva_eve_evento_fk=evento
        )

        # Eliminar archivo si existe
        ruta_documento = evaluador_evento.eva_eve_documentos
        if ruta_documento:
            ruta_documento_path = os.path.join(settings.MEDIA_ROOT, 'uploads', ruta_documento)
            if os.path.exists(ruta_documento_path):
                os.remove(ruta_documento_path)

        # Guardar correo para enviar notificación
        correo = evaluador.usuario.email

        # Eliminar la relación evaluador-evento
        evaluador_evento.delete()

        # Si no tiene más eventos asignados, eliminar el evaluador
        if not evaluador.eventos.exists():
            evaluador.delete()

        messages.success(request, "Asignación cancelada y evaluador eliminado exitosamente.")

        # Enviar correo de notificación
        if correo:
            asunto = f"Cancelación de asignación en el evento {evento.eve_nombre}"
            mensaje = (
                f"Hola {evaluador.usuario.first_name},\n\n"
                f"Tu asignación como evaluador en el evento '{evento.eve_nombre}' ha sido cancelada.\n"
                f"Gracias por tu participación."
            )
            enviar_correo(correo, asunto, mensaje)

    except EvaluadorEventos.DoesNotExist:
        messages.error(request, "No estás asignado a este evento como evaluador.")
    except Evaluador.DoesNotExist:
        messages.error(request, "Evaluador no encontrado.")
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")

    return redirect('qr:consulta_qr')





def gestionar_inscripciones(request, eve_id):
    """Gestionar inscripciones de participantes por parte de un evaluador"""

    if 'usuario_id' not in request.session:
        messages.error(request, "Debes iniciar sesión para continuar.")
        return redirect('login')

    if request.session.get('rol') != 'EVALUADOR':
        messages.warning(request, "Acceso restringido solo a evaluadores.")
        return redirect('inicio')

    try:
        evaluador = Evaluador.objects.get(usuario__id=request.session['usuario_id'])
    except Evaluador.DoesNotExist:
        messages.error(request, "No se encontró información como evaluador.")
        return redirect('inicio')

    asignacion = EvaluadorEventos.objects.filter(
        eva_eve_evaluador_fk=evaluador,
        eva_eve_evento_fk=eve_id,
        eva_estado='ACEPTADO'
    ).first()

    if not asignacion:
        messages.warning(request, "No estás asignado a este evento o tu acceso aún no ha sido aprobado.")
        return redirect('inicio')

    request.session['evento_actual_id'] = eve_id

    evento = get_object_or_404(Evento, pk=eve_id)

    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=eve_id
    ).select_related('par_eve_participante_fk')

    participantes = [
        {
            'par_id': pe.par_eve_participante_fk.par_id,
            'par_nombre': pe.par_eve_participante_fk.par_nombre,
            'par_correo': pe.par_eve_participante_fk.par_correo,
            'par_estado': pe.par_estado,
            'par_eve_documentos': pe.par_eve_documentos
        }
        for pe in participantes_eventos
    ]

    return render(request, "app_evaluadores/ver_participantes.html", {
        'evento': evento,
        'participantes': participantes
    })