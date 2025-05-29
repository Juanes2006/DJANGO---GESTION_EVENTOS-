from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from app_eventos.models import Evento
from app_registros.models import AsistentesEventos
from app_participantes.models import ParticipantesEventos, Participantes
from app_registros.models import Asistentes
import segno, base64
from io import BytesIO

def consulta_qr(request):
    events = Evento.objects.all()

    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        user_id = request.POST.get('user_id')

        if not event_id or not user_id:
            messages.warning(request, "Debes seleccionar un evento y escribir tu documento.")
            return redirect('qr:consulta_qr')  # Usa el namespace si lo tienes

        # Buscar usuario
        usuario = Asistentes.objects.filter(pk=user_id).first() or Participantes.objects.filter(pk=user_id).first()

        if usuario:
            messages.success(request, "Usuario encontrado")
        else:
            messages.error(request, "Usuario no encontrado")

        return redirect('qr:mostrar_qr', event_id=event_id, user_id=user_id)

    return render(request,'app_qr/consulta_qr.html', {'events': events})


def mostrar_qr(request, event_id, user_id):
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
        messages.error(request, "No estás registrado como Asistente ni Participante en este evento.")
        return redirect('qr:consulta_qr')

    if participante_evento and participante_evento.par_estado != "ACEPTADO":
        messages.error(request, "Tu inscripción aún no ha sido aceptada. No puedes obtener el QR.")
        return redirect('qr:consulta_qr')

    if asistente_evento and asistente_evento.asi_eve_estado != "ACEPTADO":
        messages.error(request, "Tu asistencia aún no ha sido confirmada. No puedes obtener el QR.")
        return redirect('qr:consulta_qr')

    if asistente_evento:
        qr_data = f"Tipo=Asistente|ID={user_id}|Evento={event_id}|Clave={asistente_evento.asi_eve_clave}"
        registration_type = "Asistente"
        user_document = asistente_evento.asi_eve_asistente_fk
    else:
        qr_data = f"Tipo=Participante|ID={user_id}|Evento={event_id}|Clave={participante_evento.par_eve_clave}"
        registration_type = "Participante"
        user_document = participante_evento.par_eve_participante_fk

    qr = segno.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=5)
    qr_bytes = buffer.getvalue()
    qr_b64 = base64.b64encode(qr_bytes).decode('utf-8')

    evento = Evento.objects.filter(pk=event_id).first()
    if not evento:
        messages.error(request, "El evento no fue encontrado.")
        return redirect('qr:consulta_qr')

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



