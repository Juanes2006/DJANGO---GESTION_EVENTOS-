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

    if usuario.rol != 'ASISTENTE':
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("main:visitante")

    eventos_inscritos = AsistentesEventos.objects.select_related('asi_eve_evento_fk')\
        .filter(asi_eve_asistente_fk__usuario=usuario)

    return render(request, "app_asistentes/panel_asistente.html", {
        "eventos_inscritos": eventos_inscritos
    })
