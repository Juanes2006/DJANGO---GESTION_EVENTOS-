from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from app_eventos.models import Evento
from app_registros.models import AsistentesEventos
from app_participantes.models import ParticipantesEventos, Participantes
from app_registros.models import Asistentes
import segno, base64
from app_evaluadores.models import EvaluadorEventos, Evaluador
from io import BytesIO
from django.contrib.auth.decorators import login_required

@login_required
def consulta_qr(request):
    user = request.user

    # Obtener el perfil correspondiente
    participante = getattr(user, 'participantes', None)
    asistente = getattr(user, 'asistentes', None)
    
    try:
        evaluador = Evaluador.objects.get(usuario=user)
    except Evaluador.DoesNotExist:
        evaluador = None

    if not (participante or asistente or evaluador):
        messages.error(request, "Tu cuenta no está registrada como participante, asistente ni evaluador.")
        return redirect('main:login_view')

    # Obtener IDs de eventos según el rol
    if participante:
        eventos_ids = ParticipantesEventos.objects.filter(
            par_eve_participante_fk=participante,
            par_estado='ACEPTADO'
        ).values_list('par_eve_evento_fk', flat=True)
        user_id = participante.pk

    elif asistente:
        eventos_ids = AsistentesEventos.objects.filter(
            asi_eve_asistente_fk=asistente
        ).values_list('asi_eve_evento_fk', flat=True)
        user_id = asistente.pk

    elif evaluador:
        eventos_ids = EvaluadorEventos.objects.filter(
            eva_eve_evaluador_fk=evaluador,
            eva_estado='ACEPTADO'
        ).values_list('eva_eve_evento_fk', flat=True)
        user_id = evaluador.pk

    else:
        eventos_ids = Evento.objects.none()
        user_id = None

    # Filtrar eventos válidos
    events = Evento.objects.filter(pk__in=eventos_ids)

    # Manejo del formulario
    if request.method == 'POST':
        event_id = request.POST.get('event_id')

        if not event_id:
            messages.warning(request, "Debes seleccionar un evento.")
            return redirect('qr:consulta_qr')

        return redirect('qr:mostrar_qr', event_id=event_id, user_id=user_id)

    return render(request, 'app_qr/consulta_qr.html', {
        'events': events
    })

@login_required
def mostrar_qr(request, event_id, user_id):
    user = request.user

    participante = getattr(user, 'participantes', None)
    asistente = getattr(user, 'asistentes', None)
    evaluador = getattr(user, 'evaluadores', None)

    evento = get_object_or_404(Evento, pk=event_id)

    autorizado = False

    if participante and participante.pk == int(user_id):
        autorizado = ParticipantesEventos.objects.filter(
            par_eve_participante_fk=participante,
            par_eve_evento_fk=evento,
            par_estado='ACEPTADO'
        ).exists()

    elif asistente and asistente.pk == int(user_id):
        autorizado = AsistentesEventos.objects.filter(
            asi_eve_asistente_fk=asistente,
            asi_eve_evento_fk=evento
        ).exists()

    elif evaluador and evaluador.pk == int(user_id):
        autorizado = EvaluadorEventos.objects.filter(
            eva_eve_evaluador_fk=evaluador,
            eva_eve_evento_fk=evento
        ).exists()

    if not autorizado:
        messages.error(request, "No estás autorizado para ver el QR de este evento.")
        return redirect('qr:consulta_qr')

    # Aquí generarías o cargarías el QR relacionado
    return render(request, 'app_qr/mostrar_qr.html', {
        'evento': evento,
        'user_id': user_id
    })
@login_required
def mostrar_qr(request, event_id, user_id):
    evento = get_object_or_404(Evento, pk=event_id)

    # Buscar si es asistente
    asistente_evento = AsistentesEventos.objects.filter(
        asi_eve_asistente_fk=user_id,
        asi_eve_evento_fk=event_id
    ).first()

    # Buscar si es participante
    participante_evento = None
    if not asistente_evento:
        participante_evento = ParticipantesEventos.objects.filter(
            par_eve_participante_fk=user_id,
            par_eve_evento_fk=event_id
        ).first()

    # Buscar si es evaluador
    evaluador_evento = None
    if not asistente_evento and not participante_evento:
        evaluador_evento = EvaluadorEventos.objects.filter(
            eva_eve_evaluador_fk=user_id,
            eva_eve_evento_fk=event_id
        ).first()

    if not asistente_evento and not participante_evento and not evaluador_evento:
        messages.error(request, "No estás registrado en este evento.")
        return redirect('qr:consulta_qr')

    # Validaciones de estado
    if participante_evento and participante_evento.par_estado != "ACEPTADO":
        messages.error(request, "Tu inscripción como participante aún no ha sido aceptada.")
        return redirect('qr:consulta_qr')

    if asistente_evento and asistente_evento.asi_eve_estado != "ACEPTADO":
        messages.error(request, "Tu asistencia aún no ha sido confirmada.")
        return redirect('qr:consulta_qr')

    # Generar el QR
    if asistente_evento:
        qr_data = f"Tipo=Asistente|ID={user_id}|Evento={event_id}|Clave={asistente_evento.asi_eve_clave}"
        registration_type = "Asistente"
        user_document = asistente_evento.asi_eve_asistente_fk

    elif participante_evento:
        qr_data = f"Tipo=Participante|ID={user_id}|Evento={event_id}|Clave={participante_evento.par_eve_clave}"
        registration_type = "Participante"
        user_document = participante_evento.par_eve_participante_fk

    else:  # evaluador_evento
        qr_data = f"Tipo=Evaluador|ID={user_id}|Evento={event_id}|Clave={evaluador_evento.eva_eve_clave}"
        registration_type = "Evaluador"
        user_document = evaluador_evento.eva_eve_evaluador_fk

    # Generar imagen QR
    qr = segno.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=5)
    qr_bytes = buffer.getvalue()
    qr_b64 = base64.b64encode(qr_bytes).decode('utf-8')
    
    

    return render(request, 'app_qr/mostrar_qr.html', {
        'qr_image': qr_b64,
        'evento': evento,
        'registration_type': registration_type,
        'user_document': user_document,
        'user_id': user_id,
    })


def descargar_qr(request, event_id, user_id):
    asistente_evento = AsistentesEventos.objects.filter(
        asi_eve_asistente_fk=user_id,
        asi_eve_evento_fk=event_id
    ).first()

    participante_evento = None
    if not asistente_evento:
        participante_evento = ParticipantesEventos.objects.filter(
            par_eve_participante_fk=user_id,
            par_eve_evento_fk=event_id
        ).first()

    if not asistente_evento and not participante_evento:
        return HttpResponse("No estás registrado en este evento.", status=404)

    if asistente_evento:
        qr_data = f"Tipo=Asistente|ID={user_id}|Evento={event_id}|Clave={asistente_evento.asi_eve_clave}"
    else:
        qr_data = f"Tipo=Participante|ID={user_id}|Evento={event_id}|Clave={participante_evento.par_eve_clave}"

    qr = segno.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=5)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename=qr_code.png'
    return response



