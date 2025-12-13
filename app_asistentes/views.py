from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import os
from app_eventos.models import Evento
from app_registros.models import AsistentesEventos
from app_participantes.models import ParticipantesEventos, Participantes
from app_registros.models import Asistentes
from app_evaluadores.models import Evaluador, EvaluadorEventos
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
from app_usuarios.models import Usuario
from django.contrib.auth.decorators import login_required

@login_required
def panel_asistente(request):
    usuario = request.user

    if not hasattr(usuario, 'rol') or usuario.rol != 'ASISTENTE':
        messages.error(request, "⛔ No tienes permiso para acceder a esta sección.")
        return redirect("main:visitante")

    eventos_inscritos = AsistentesEventos.objects.select_related('asi_eve_evento_fk')\
        .filter(asi_eve_asistente_fk__usuario=usuario)

    return render(request, "app_asistentes/panel_asistente.html", {
        "eventos_inscritos": eventos_inscritos
    })

    
from app_eventos.models import MemoriaEvento
@login_required
def ver_memorias_evento_asis(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    inscrito = AsistentesEventos.objects.filter(
        asi_eve_asistente_fk__usuario=request.user,
        asi_eve_evento_fk=evento
    ).exists()

    if not inscrito:
        messages.error(request, "No tienes acceso a las memorias de este evento.")
        return redirect('main:lista_eventos')

    memorias = MemoriaEvento.objects.filter(evento=evento)

    return render(request, "app_asistentes/memorias_evento.html", {
        "evento": evento,
        "memorias": memorias
    })

@login_required
def modificar_asistente(request, user_id, evento_id):
    asistente = get_object_or_404(Participantes, pk=user_id)
    evento_asistente = get_object_or_404(
        AsistentesEventos,
        asi_eve_asistente_fk=asistente,
        asi_eve_evento_fk=evento_id
    )
    evento = get_object_or_404(Evento, pk=evento_id)


        # SOPORTE DE PAGO (Cloudinary)
        
    if request.method == 'POST':
        usuario = asistente.usuario
        usuario.first_name = request.POST.get('nombre')
        usuario.email = request.POST.get('correo')
        usuario.telefono = request.POST.get('telefono')
        usuario.save()

        file = request.FILES.get('soporte')
        if file:
            evento_asistente.asi_eve_soporte = file

        evento_asistente.save()

        messages.success(request, "Información actualizada con éxito")
        return redirect('asistente:panel_asistente')

    return render(request, "app_asistentes/modificar_asistente.html", {
        "asistente": asistente,
        "evento_asistente": evento_asistente,
        'evento_nombre': evento.eve_nombre,
    })
    

