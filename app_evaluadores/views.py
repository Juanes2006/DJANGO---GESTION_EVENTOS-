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


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail


def enviar_correo(destinatario, asunto, mensaje):
    email_desde = settings.EMAIL_HOST_USER
    destinatarios = [destinatario]
    send_mail(asunto, mensaje, email_desde, destinatarios, fail_silently=False)



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

        return redirect(reverse('admin_evento:gestionar_criterios_admin', args=[evento_id]))

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



######################## NUEVAS


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
    # Obtener evaluador por su ID
    evaluador = get_object_or_404(Evaluador, pk=user_id)
    
    # Obtener la asignación evaluador-evento (evaluadoreventos)
    asignacion = EvaluadorEventos.objects.filter(
        eva_eve_evaluador_fk=user_id,
        eva_eve_evento_fk=evento_id
    ).first()
    
    if not asignacion:
        messages.error(request, "No se encontró la asignación para este evaluador en el evento.")
        return redirect('evaluadores:mi_info')  # O la URL que corresponda
    
    if request.method == 'POST':
        # Actualiza campos del evaluador (ajusta según tus campos)
        evaluador.nombre = request.POST.get('nombre')
        evaluador.correo = request.POST.get('correo')
        evaluador.telefono = request.POST.get('telefono')
        
        # Si manejas archivos (por ejemplo documentos)
        file = request.FILES.get('documento')
        if file:
            filename = save_file(file, settings.UPLOAD_FOLDER_PAGOS, settings.ALLOWED_EXTENSIONS_PAGOS)
            if filename:
                evaluador.par_eve_documentos = filename
            else:
                messages.warning(request, "Extensión no permitida o error al guardar el archivo")
        evaluador.save()
        asignacion.save()
        
        messages.success(request, "Información del evaluador actualizada correctamente.")
        return redirect('evaluadores:mi_info')  # O donde quieras redirigir
    
    context = {
        'evaluador': evaluador,
        'asignacion': asignacion,
        'evento_nombre': asignacion.eva_eve_evento_fk.eve_nombre,
    }
    return render(request, 'app_evaluadores/modificar_evaluador.html', context)



def mi_info(request):
    eventos = Evento.objects.all().prefetch_related('criterios')
    
    evaluador = None
    eventos_asignados = []
    
    if request.method == 'POST':
        eva_id = request.POST.get('eva_id')
        print("ID Evaluador:", eva_id)
        
        if eva_id:
            evaluador = Evaluador.objects.filter(eva_id=eva_id).first()
            print("Evaluador encontrado:", evaluador)
            
            if evaluador:
                # MÉTODO ALTERNATIVO: Consulta directa desde EvaluadorEvento
                
                asignaciones = EvaluadorEventos.objects.filter(
                    eva_eve_evaluador_fk=eva_id,
                    eva_eve_evento_fk__eve_estado="ACTIVO"
                ).select_related('eva_eve_evento_fk')
                
                print(f"Asignaciones encontradas: {asignaciones.count()}")
                
                for asignacion in asignaciones:
                    eve_id = asignacion.eva_eve_evento_fk.eve_id
                    
                    print(f"Evento: {asignacion.eva_eve_evento_fk.eve_nombre}")
                    print(f"Estado: {asignacion.eva_estado}")
                    print(f"Documento: '{asignacion.eva_eve_documentos}'")
                    print("---")
                    
                    # Aquí puedes agregar el resto de la lógica de puntajes, etc.
                    # Por ahora solo lo básico para probar
                    
                    eventos_asignados.append({
                        'evento': {
                            'eve_id': eve_id,
                            'eve_nombre': asignacion.eva_eve_evento_fk.eve_nombre,
                            'eve_fecha_inicio': asignacion.eva_eve_evento_fk.eve_fecha_inicio,
                            'eve_ciudad': asignacion.eva_eve_evento_fk.eve_ciudad,
                        },
                        'eva_estado': asignacion.eva_estado,
                        'eva_eve_documentos': asignacion.eva_eve_documentos,
                        'puntaje_total': 0,  # Temporal
                        'promedio': 0,       # Temporal
                        'posicion': None,    # Temporal
                        'instrumento': None, # Temporal
                        'criterios': [],     # Temporal
                    })
            else:
                messages.error(request, "No se encontró información para el ID del evaluador.")
    
    return render(request, "app_evaluadores/eva_informacion.html", {
        'titulo': "Mis Eventos Asignados",
        'evaluador': evaluador,
        'eventos_asignados': eventos_asignados,
    })


def cancelar_inscripcion(request, evento_id, user_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    correo = None

    try:
        evaluador_evento = EvaluadorEventos.objects.get(
            eva_eve_evaluador_fk__eva_id=user_id,
            eva_eve_evento_fk=evento
        )
        ruta_documento = evaluador_evento.eva_eve_documentos

        # Eliminar documento si existe
        if ruta_documento:
            ruta_documento_path = os.path.join(settings.MEDIA_ROOT, 'uploads', ruta_documento)
            if os.path.exists(ruta_documento_path):
                os.remove(ruta_documento_path)

        correo = evaluador_evento.eva_eve_evaluador_fk.eva_correo

        # Eliminar el evaluador si no tiene más asignaciones
        evaluador = evaluador_evento.eva_eve_evaluador_fk
        evaluador_evento.delete()

        if not evaluador.eventos.exists():  # Sin más relaciones
            evaluador.delete()

        messages.success(request, "Asignación cancelada y evaluador eliminado exitosamente.")

        # Enviar correo de confirmación
        if correo:
            asunto = f"Cancelación de asignación en el evento {evento.eve_nombre}"
            mensaje = f"Hola,\n\nTu asignación como evaluador en el evento '{evento.eve_nombre}' ha sido cancelada correctamente."
            enviar_correo(correo, asunto, mensaje)

    except EvaluadorEventos.DoesNotExist:
        messages.error(request, "No estás asignado a este evento como evaluador.")

    return redirect('qr:consulta_qr')





def gestionar_inscripciones(request, eve_id):
    """Gestionar inscripciones de participantes"""
    evento = get_object_or_404(Evento, pk=eve_id)
    
    # Query similar to the Flask SQLAlchemy join
    participantes_eventos = ParticipantesEventos.objects.filter(
        par_eve_evento_fk=eve_id
    ).select_related('par_eve_participante_fk')
    
    participantes = []
    for pe in participantes_eventos:
        participantes.append({
            'par_id': pe.par_eve_participante_fk.par_id,
            'par_nombre': pe.par_eve_participante_fk.par_nombre,
            'par_correo': pe.par_eve_participante_fk.par_correo,
            'par_estado': pe.par_estado,
            'par_eve_documentos': pe.par_eve_documentos
        })
    
    return render(request, "app_evaluadores/ver_participantes.html", {
        'evento': evento,
        'participantes': participantes
    })