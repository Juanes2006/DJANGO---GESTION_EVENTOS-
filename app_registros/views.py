from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import os
from .forms import RegistroEventoForm
from app_eventos.models import Evento
from app_registros.models import AsistentesEventos
from app_participantes.models import ParticipantesEventos, Participantes
from app_registros.models import Asistentes
from app_evaluadores.models import Evaluador, EvaluadorEventos
from datetime import datetime
from django.conf import settings


import os
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# Función para enviar correo
def enviar_correo(destinatario, asunto, mensaje):
    email_desde = settings.EMAIL_HOST_USER
    destinatarios = [destinatario]
    send_mail(asunto, mensaje, email_desde, destinatarios, fail_silently=False)


def registrarme_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == 'POST':
        form = RegistroEventoForm(request.POST, request.FILES)
        if form.is_valid():
            tipo = form.cleaned_data['tipo_inscripcion']
            user_id = form.cleaned_data['user_id']
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            telefono = form.cleaned_data['telefono']
            soporte_pago = form.cleaned_data.get('soporte_pago')
            documentos = form.cleaned_data.get('documentos')

            if tipo == 'Asistente':
                asistente, created = Asistentes.objects.get_or_create(
                    asi_id=user_id,
                    defaults={'asi_nombre': nombre, 'asi_correo': correo, 'asi_telefono': telefono}
                )

                soporte_pago_filename = None
                if evento.cobro.lower() in ['sí', 'si'] and soporte_pago:
                    soporte_pago_filename = soporte_pago.name
                    soporte_pago_path = os.path.join(settings.MEDIA_ROOT, 'static/uploads', soporte_pago_filename)
                    with open(soporte_pago_path, 'wb+') as destination:
                        for chunk in soporte_pago.chunks():
                            destination.write(chunk)

                clave_asis = user_id[::-1]

                AsistentesEventos.objects.create(
                    asi_eve_asistente_fk=asistente,
                    asi_eve_evento_fk=evento,
                    asi_eve_fecha_hora=datetime.utcnow(),
                    asi_eve_soporte=soporte_pago_filename,
                    asi_eve_estado='Registrado',
                    asi_eve_clave=clave_asis
                )

            elif tipo == 'Participante':
                participante, created = Participantes.objects.get_or_create(
                    par_id=user_id,
                    defaults={'par_nombre': nombre, 'par_correo': correo, 'par_telefono': telefono}
                )

                documentos_filename = None
                if documentos:
                    documentos_filename = documentos.name
                    documentos_path = os.path.join(settings.MEDIA_ROOT, 'static/uploads', documentos_filename)
                    with open(documentos_path, 'wb+') as destination:
                        for chunk in documentos.chunks():
                            destination.write(chunk)

                clave_par = user_id[::-1]

                ParticipantesEventos.objects.create(
                    par_eve_participante_fk=participante,
                    par_eve_evento_fk=evento,
                    par_eve_fecha_hora=datetime.utcnow(),
                    par_eve_documentos=documentos_filename,
                    par_eve_or=clave_par,
                    par_eve_clave=clave_par
                )
                
                
            elif tipo == 'Evaluador':
                evaluador, evaluador_created = Evaluador.objects.get_or_create(
                    eva_id=user_id,
                    defaults={'eva_nombre': nombre, 'eva_correo': correo, 'eva_telefono': telefono}
                )

                documentos_filename = None
                if documentos:
                    documentos_filename = documentos.name
                    documentos_path = os.path.join(settings.MEDIA_ROOT, 'static/uploads', documentos_filename)
                    with open(documentos_path, 'wb+') as destination:
                        for chunk in documentos.chunks():
                            destination.write(chunk)

                clave_eva = user_id[::-1]

                # Usar get_or_create para evitar duplicados
                evaluador_evento, evento_created = EvaluadorEventos.objects.get_or_create(
                    eva_eve_evaluador_fk=evaluador,
                    eva_eve_evento_fk=evento,
                    defaults={
                        'eva_eve_fecha_hora': datetime.utcnow(),
                        'eva_eve_documentos': documentos_filename,
                        'eva_eve_or': clave_eva,
                        'eva_eve_clave': clave_eva,
                        'eva_estado': 'PENDIENTE'
                    }
                )

                if evento_created:  # ✅ Verificar si se creó el registro del evento
                        messages.success(request, "¡Te has preinscrito exitosamente como Evaluador!")
                else:
                    messages.info(request, "Ya estás registrado como evaluador en este evento.")

            messages.success(request, f"¡Te has preinscrito exitosamente como {tipo}!")

            # Enviar correo de confirmación
            asunto = f"Confirmación de registro en {evento.eve_nombre}"
            mensaje = f"Hola {nombre}\n\nTe has preinscrito exitosamente como {tipo} en el evento '{evento.eve_nombre}'.\n¡Confirmemos tus datos!\nDocumento : {user_id}\nNombre: {nombre}\nCorreo: {correo}\nTelefono: {telefono}\n¡Espera tu confirmacion!\n¡Gracias por tu participación!"
            enviar_correo(correo, asunto, mensaje)

            return redirect('main:lista_eventos')
    else:
        form = RegistroEventoForm()

    return render(request, 'app_registros/formulario_registro.html', {'form': form, 'evento': evento})


def cancelar_inscripcion(request, evento_id, user_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    try:
        asistente_evento = AsistentesEventos.objects.get(
            asi_eve_asistente_fk__asi_id=user_id,
            asi_eve_evento_fk=evento
        )
        ruta_archivo = asistente_evento.asi_eve_soporte
        if ruta_archivo:
            ruta_archivo_path = os.path.join(settings.MEDIA_ROOT, 'uploads', ruta_archivo)
            if os.path.exists(ruta_archivo_path):
                os.remove(ruta_archivo_path)
        correo = asistente_evento.asi_eve_asistente_fk.asi_correo
        asistente_evento.asi_eve_asistente_fk.delete()
        asistente_evento.delete()
        messages.success(request, "Inscripción cancelada y usuario eliminado exitosamente.")

    except AsistentesEventos.DoesNotExist:
        try:
            participante_evento = ParticipantesEventos.objects.get(
                par_eve_participante_fk__par_id=user_id,
                par_eve_evento_fk=evento
            )
            ruta_documento = participante_evento.par_eve_documentos
            if ruta_documento:
                ruta_documento_path = os.path.join(settings.MEDIA_ROOT, 'uploads', ruta_documento)
                if os.path.exists(ruta_documento_path):
                    os.remove(ruta_documento_path)
            correo = participante_evento.par_eve_participante_fk.par_correo
            participante_evento.par_eve_participante_fk.delete()
            participante_evento.delete()
            messages.success(request, "Inscripción cancelada y usuario eliminado exitosamente.")
        except ParticipantesEventos.DoesNotExist:
            messages.error(request, "No estás registrado en este evento.")
            return redirect('qr:consulta_qr')

    # Enviar correo de confirmación de cancelación
    if correo:
        asunto = f"Confirmación de cancelación en {evento.eve_nombre}"
        mensaje = f"Hola,\n\nTu inscripción en el evento '{evento.eve_nombre}' ha sido cancelada correctamente."
        enviar_correo(correo, asunto, mensaje)

    return redirect('qr:consulta_qr')
