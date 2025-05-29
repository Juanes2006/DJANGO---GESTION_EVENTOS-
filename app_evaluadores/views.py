from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, F, Q
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


from app_eventos.models import Evento
from app_participantes.models import Participantes, ParticipantesEventos
from app_evaluadores.models import Criterio, Instrumento, Calificacion, Evaluador


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

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
def seleccionar_evento(request):
    evaluador_id = request.session.get('evaluador_id')
    if not evaluador_id:
        messages.warning(request, 'Debes iniciar sesión primero.')
        return redirect('evaluadores:login_evaluador')

    evaluador = get_object_or_404(Evaluador, pk=evaluador_id)

    eventos = Evento.objects.filter(evaluadores=evaluador).distinct()

    return render(request, 'app_evaluadores/seleccionar_evento.html', {
        'eventos': eventos,
        'evaluador': evaluador
    })



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

        return redirect(reverse('admin:gestionar_criterios_admin', args=[evento_id]))

    total_peso = criterios.aggregate(total=Sum('cri_peso'))['total'] or 0

    return render(request, 'app_evaluadores/criterios.html', {
        'criterios': criterios,
        'instrumento': instrumento,
        'evento_id': evento_id,
        'total_peso': round(total_peso, 2),
        'evento': evento
    })


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


# --- Lista participantes ---

def lista_participantes(request, eva_id, evento_id):
    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=evento_id,
        par_estado='ACEPTADO'
    )
    participantes = [pe.par_eve_participante_fk for pe in participantes_eventos]

    return render(request, 'app_evaluadores/lista_participantes.html', {
        'eva_id': eva_id,
        'evento_id': evento_id,
        'participantes': participantes
    })



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



# --- Ver ranking ---
def ver_ranking(request, eva_id, evento_id):
    evaluador = get_object_or_404(Evaluador, pk=eva_id)
    evento = get_object_or_404(Evento, pk=evento_id)

    # Calcular suma ponderada de calificaciones (cal_valor * cri_peso)
    ranking = (
        Participantes.objects.filter(
            calificacion__cal_criterio_fk__cri_evento_fk=evento
        )
        .annotate(
            puntaje_total=Sum(F('calificacion__cal_valor') * F('calificacion__cal_criterio_fk__cri_peso')/100)
        )
        .order_by('-puntaje_total')
        .distinct()
    )

    return render(request, 'app_evaluadores/ranking.html', {
        'evaluador': evaluador,
        'evento': evento,
        'ranking': ranking
    })


# --- Login evaluador ---
def login_evaluador(request):
    if request.method == 'POST':
        eva_id = request.POST.get('eva_id')
        evaluador = Evaluador.objects.filter(pk=eva_id).first()
        if evaluador:
            request.session['evaluador_id'] = evaluador.eva_id
            messages.success(request, 'Inicio de sesión exitoso')
            return redirect('evaluadores:seleccionar_evento')
        else:
            messages.error(request, 'Evaluador no encontrado, verifica tus datos')
            return redirect('evaluadores:login_evaluador')

    return render(request, 'app_evaluadores/login.html')


# --- Logout evaluador ---
def logout_evaluador(request):
    request.session.pop('evaluador_id', None)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('evaluadores:login_evaluador')


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


# --- Ver calificaciones participante ---
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

    return render(request, 'app_evaluadores/calificaciones_participante.html', context)
