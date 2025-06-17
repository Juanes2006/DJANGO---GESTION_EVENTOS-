from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, F

from app_eventos.models import Evento
from app_participantes.models import Participantes, ParticipantesEventos
from app_evaluadores.models import Criterio, Instrumento, Calificacion, Evaluador


from .utils import save_file  

def verificar_participante(request):
    if request.method == 'POST':
        par_id = request.POST.get('par_id')
        if not par_id:
            messages.warning(request, "Por favor, ingresa tu ID de participante.")
            return redirect('participantes:verificar_participante')

        try:
            participante = Participantes.objects.get(pk=par_id)
        except Participantes.DoesNotExist:
            messages.error(request, "No se encontró un participante con este ID.")
            return redirect('participantes:verificar_participante')

        return redirect('participantes:modificar_participante', user_id=par_id, evento_id=1)  

    return render(request, 'app_participantes/verificar_participante.html')

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


def mi_info(request):
    eventos = Evento.objects.all().prefetch_related('criterios')

    participante = None
    eventos_inscritos = []

    if request.method == 'POST':
        par_id = request.POST.get('par_id')
        print("PART encontrado:", participante)
        if par_id:
            participante = Participantes.objects.filter(par_id=par_id).first()
            if participante:
                inscripciones = Evento.objects.filter(
                    eve_estado="ACTIVO",
                    participanteseventos__par_eve_participante_fk=par_id
                ).values(
                    'eve_id', 'eve_nombre', 'eve_fecha_inicio', 'eve_ciudad',
                    'participanteseventos__par_estado',
                    'participanteseventos__par_eve_documentos'
                )

                for inscripcion in inscripciones:
                    eve_id = inscripcion['eve_id']

                    # 1. Puntaje total del participante en este evento
                    puntaje_total = Calificacion.objects.filter(
                        cal_participante_fk=par_id,
                        cal_criterio_fk__cri_evento_fk=eve_id
                    ).aggregate(total=Sum('cal_valor'))['total'] or 0

                    # 2. Ranking general
                    participantes_puntajes = Calificacion.objects.filter(
                        cal_criterio_fk__cri_evento_fk=eve_id
                    ).values('cal_participante_fk').annotate(
                        total_puntaje=Sum('cal_valor')
                    ).order_by('-total_puntaje')

                    posicion = None
                    for idx, p in enumerate(participantes_puntajes, start=1):
                        if str(p['cal_participante_fk']) == str(par_id):
                            posicion = idx
                            break

                    # 3. Instrumento relacionado
                    instrumento = Instrumento.objects.filter(inst_evento_fk=eve_id).first()
                    criterios = Criterio.objects.filter(cri_evento_fk=eve_id)

                    # 4. Promedio del puntaje
                    criterios_count = criterios.count()
                    promedio = puntaje_total / criterios_count if criterios_count > 0 else 0

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
                        'promedio': round(promedio, 2),  # ✅ Incluido aquí
                        'posicion': posicion,
                        'instrumento': instrumento,
                        'criterios': criterios,
                    })
            else:
                messages.error(request, "No se encontró información para el ID proporcionado.")

    return render(request, "app_participantes/par_informacion.html", {
        'titulo': "Mis Eventos Inscritos",
        'participante': participante,
        'eventos_inscritos': eventos_inscritos,
    })

def ver_instrumento(request, evento_id):
    criterios = Criterio.objects.filter(cri_evento_fk=evento_id)
    return render(request, 'app_participantes/instrumento.html', {'criterios': criterios})

def ver_calificaciones(request, participante_id):
    calificaciones = Calificacion.objects.filter(cal_participante_fk=participante_id)
    puntaje_total = sum(cal.cal_valor for cal in calificaciones)

    return render(request, 'app_participantes/calificaciones.html', {
        'calificaciones': calificaciones,
        'puntaje_total': puntaje_total,
    })

def ranking_participantes(request, evento_id):
    participantes = Participantes.objects.filter(par_evento_fk=evento_id)
    ranking = []

    for participante in participantes:
        puntajes = Calificacion.objects.filter(cal_participante_fk=participante.par_id)
        total_puntaje = sum(p.cal_valor for p in puntajes)
        ranking.append({'participante': participante, 'total_puntaje': total_puntaje})

    ranking.sort(key=lambda x: x['total_puntaje'], reverse=True)

    return render(request, 'app_participantes/ranking.html', {'ranking': ranking})

def ver_calificaciones_participante(request, evento_id, participante_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    participante = get_object_or_404(Participantes, pk=participante_id)

    calificaciones = Calificacion.objects.filter(
        cal_participante_fk=participante_id,
        cal_criterio_fk__cri_evento_fk=evento_id
    ).select_related('cal_criterio_fk', 'cal_evaluador_fk').values(
        'cal_criterio_fk__cri_descripcion',
        'cal_evaluador_fk__eva_nombre',
        'cal_valor'
    )

    return render(request, 'app_participantes/calificaciones_participante.html', {
        'evento': evento,
        'participante': participante,
        'calificaciones': calificaciones,
    })
