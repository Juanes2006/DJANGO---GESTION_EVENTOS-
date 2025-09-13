from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, F

from app_eventos.models import Evento
from app_participantes.models import Participantes, ParticipantesEventos
from app_evaluadores.models import Criterio, Instrumento, Calificacion, Evaluador
from app_participantes.models import Participantes, ParticipantesEventos
from django.contrib.auth.decorators import login_required
from app_eventos.models import MemoriaEvento

from .utils import save_file  

@login_required
def panel_participante(request):
    usuario = request.user

    if usuario.rol != 'PARTICIPANTE':
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("main:index")

    eventos_inscritos = ParticipantesEventos.objects.select_related('par_eve_evento_fk', 'proyecto')\
        .filter(par_eve_participante_fk__usuario=usuario)
        
    eventos = eventos_inscritos.values_list('par_eve_evento_fk', flat=True)
    memorias = MemoriaEvento.objects.filter(evento__in=eventos)
    
    
    for inscripcion in eventos_inscritos:
        if inscripcion.proyecto:
            inscripcion.proyecto_companeros = inscripcion.proyecto.participantes.exclude(pk=usuario.pk)
            inscripcion.es_creador = (inscripcion.proyecto.creador == usuario)
        else:
            inscripcion.proyecto_companeros = []
            inscripcion.es_creador = False
    
    return render(request, "app_participantes/panel_participante.html", {
        "eventos_inscritos": eventos_inscritos, "memorias": memorias
    })
    
    
    
@login_required
def ver_memorias_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    inscrito = ParticipantesEventos.objects.filter(
        par_eve_participante_fk__usuario=request.user,
        par_eve_evento_fk=evento
    ).exists()

    if not inscrito:
        messages.error(request, "No tienes acceso a las memorias de este evento.")
        return redirect('main:lista_eventos')

    memorias = MemoriaEvento.objects.filter(evento=evento)

    return render(request, "app_participantes/memorias_evento.html", {
        "evento": evento,
        "memorias": memorias
    })




@login_required

def modificar_participante(request, user_id, evento_id):
    participante = get_object_or_404(Participantes, pk=user_id)
    evento_participante = ParticipantesEventos.objects.filter(
        par_eve_participante_fk=user_id,
        par_eve_evento_fk=evento_id
    ).first()
    evento = get_object_or_404(Evento, pk=evento_id)

    if not evento_participante:
        messages.error(request, "No se encontró la inscripción para este evento.")
        return redirect('consulta_qr')  # Ajusta esta URL si es necesario

    if request.method == 'POST':
        participante.par_nombre = request.POST.get('nombre')
        participante.par_correo = request.POST.get('correo')
        participante.par_telefono = request.POST.get('telefono')

        file = request.FILES.get('documento')
        if file:
            filename = save_file(file, settings.UPLOAD_FOLDER_PAGOS, settings.ALLOWED_EXTENSIONS_PAGOS)
            if filename:
                evento_participante.par_eve_documentos = filename
            else:
                messages.warning(request, "Extensión no permitida o error al guardar el archivo")

        participante.save()
        evento_participante.save()
        messages.success(request, "Información actualizada con éxito")
        return redirect('participantes:mi_info')

    context = {
        'participante': participante,
        'evento_participante': evento_participante,
        'evento_nombre': evento.eve_nombre,
    }
    return render(request, 'app_participantes/modificar_participante.html', context)


@login_required
def mi_info(request):
    eventos_inscritos = []

    # 1. Obtener participante desde usuario autenticado
    try:
        participante = Participantes.objects.get(usuario=request.user)
    except Participantes.DoesNotExist:
        messages.error(request, "No se encontró información asociada al usuario.")
        return render(request, "app_participantes/par_informacion.html", {
            'participante': None,
            'eventos_inscritos': [],
        })

    # 2. Consultar eventos en los que está inscrito
    inscripciones = Evento.objects.filter(
        eve_estado="ACTIVO",
        participanteseventos__par_eve_participante_fk=participante.id
    ).values(
        'eve_id', 'eve_nombre', 'eve_fecha_inicio', 'eve_ciudad',
        'participanteseventos__par_estado',
        'participanteseventos__par_eve_documentos'
    )

    for inscripcion in inscripciones:
        eve_id = inscripcion['eve_id']

        # 3. Calcular puntaje total del participante
        puntaje_total = Calificacion.objects.filter(
            cal_participante_fk=participante.id,
            cal_criterio_fk__cri_evento_fk=eve_id
        ).aggregate(total=Sum('cal_valor'))['total'] or 0

        # 4. Calcular posición en el ranking del evento
        participantes_puntajes = Calificacion.objects.filter(
            cal_criterio_fk__cri_evento_fk=eve_id
        ).values('cal_participante_fk').annotate(
            total_puntaje=Sum('cal_valor')
        ).order_by('-total_puntaje')

        posicion = None
        for idx, p in enumerate(participantes_puntajes, start=1):
            if str(p['cal_participante_fk']) == str(participante.id):
                posicion = idx
                break

        # 5. Obtener instrumento y criterios
        instrumento = Instrumento.objects.filter(inst_evento_fk=eve_id).first()
        criterios = list(Criterio.objects.filter(cri_evento_fk=eve_id))
        criterios_count = len(criterios)
        promedio = puntaje_total / criterios_count if criterios_count > 0 else 0

        # 6. Agregar evento a la lista
        eventos_inscritos.append({
            'evento': {
                'eve_id': eve_id,
                'eve_nombre': inscripcion['eve_nombre'],
                'eve_fecha_inicio': inscripcion['eve_fecha_inicio'],
                'eve_ciudad': inscripcion['eve_ciudad'],
            },
            'par_estado': inscripcion['participanteseventos__par_estado'],
            'par_eve_documentos': inscripcion['participanteseventos__par_eve_documentos'],
            'puntaje_total': puntaje_total,
            'promedio': round(promedio, 2),
            'posicion': posicion,
            'instrumento': instrumento,
            'criterios': criterios,
        })

    return render(request, "app_participantes/par_informacion.html", {
        'titulo': "Mis Eventos Inscritos",
        'participante': participante,
        'eventos_inscritos': eventos_inscritos,
    })
    
@login_required

def ver_instrumento(request, evento_id):
    criterios = Criterio.objects.filter(cri_evento_fk=evento_id)
    return render(request, 'app_participantes/instrumento.html', {'criterios': criterios})
@login_required

def ver_calificaciones(request, participante_id):
    calificaciones = Calificacion.objects.filter(cal_participante_fk=participante_id)
    puntaje_total = sum(cal.cal_valor for cal in calificaciones)

    return render(request, 'app_participantes/calificaciones.html', {
        'calificaciones': calificaciones,
        'puntaje_total': puntaje_total,
    })
@login_required

def ranking_participantes(request, evento_id):
    participantes = Participantes.objects.filter(par_evento_fk=evento_id)
    ranking = []

    for participante in participantes:
        puntajes = Calificacion.objects.filter(cal_participante_fk=participante.par_id)
        total_puntaje = sum(p.cal_valor for p in puntajes)
        ranking.append({'participante': participante, 'total_puntaje': total_puntaje})

    ranking.sort(key=lambda x: x['total_puntaje'], reverse=True)

    return render(request, 'app_participantes/ranking.html', {'ranking': ranking})
@login_required

def ver_calificaciones_participante(request, evento_id, participante_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    participante = get_object_or_404(Participantes, pk=participante_id)

    calificaciones = Calificacion.objects.filter(
        cal_criterio_fk__cri_evento_fk=evento,
        cal_participante_fk=participante
    ).select_related('cal_criterio_fk', 'cal_evaluador_fk')

    context = {
        'evento': evento,
        'participante': participante,
        'calificaciones': calificaciones
    }

    return render(request, 'app_participantes/calificaciones_participante.html', context)

