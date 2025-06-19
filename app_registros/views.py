from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import os
from .forms import RegistroEventoForm
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
            tipo = form.cleaned_data['tipo_inscripcion'].lower()  # Normalizamos a minúsculas
            user_id = form.cleaned_data['user_id']
            username = form.cleaned_data['username']
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            telefono = form.cleaned_data['telefono']
            
            # Validaciones de datos duplicados
            if Usuario.objects.filter(username=username).exclude(pk=user_id).exists():
                messages.error(request, "El nombre de usuario ya está en uso.")
                return redirect(request.path)

            if Usuario.objects.filter(email=correo).exclude(pk=user_id).exists():
                messages.error(request, "El correo electrónico ya está en uso.")
                return redirect(request.path)
            
            if Usuario.objects.filter(telefono=telefono).exclude(pk=user_id).exists():
                messages.error(request, "Este telefono  ya está en uso.")
                return redirect(request.path)
            


            # Crear o actualizar usuario
            usuario, created = Usuario.objects.get_or_create(
                pk=user_id,
                defaults={
                    'username': username,
                    'first_name': nombre,
                    'email': correo,
                }
            )
            if not created:
                usuario.username = username
                usuario.first_name = nombre
                usuario.email = correo

            usuario.telefono = telefono
            usuario.rol = tipo.upper()  # 'ASISTENTE', 'PARTICIPANTE', 'EVALUADOR'
            usuario.save()

            # Archivos
            soporte_pago_file = request.FILES.get('soporte_pago')
            documentos_part_file = request.FILES.get('documentos_participante')
            documentos_eval_file = request.FILES.get('documentos_evaluador')

            if tipo == 'asistente':
                asistente, _ = Asistentes.objects.get_or_create(usuario=usuario)

                ya_registrado = AsistentesEventos.objects.filter(
                    asi_eve_asistente_fk=asistente,
                    asi_eve_evento_fk=evento
                ).exists()
                if not ya_registrado:
                    soporte_pago_filename = guardar_archivo(soporte_pago_file) if soporte_pago_file else None
                    clave_asis = str(usuario.pk)[::-1]

                    AsistentesEventos.objects.create(
                        asi_eve_asistente_fk=asistente,
                        asi_eve_evento_fk=evento,
                        asi_eve_fecha_hora=datetime.utcnow(),
                        asi_eve_soporte=soporte_pago_filename,
                        asi_eve_estado='Registrado',
                        asi_eve_clave=clave_asis
                    )
                    messages.success(request, "¡Te has preinscrito exitosamente como Asistente!")
                else:
                    messages.info(request, "Ya estás registrado como asistente en este evento.")

            elif tipo == 'participante':
                participante, _ = Participantes.objects.get_or_create(usuario=usuario)

                ya_registrado = ParticipantesEventos.objects.filter(
                    par_eve_participante_fk=participante,
                    par_eve_evento_fk=evento
                ).exists()
                if not ya_registrado:
                    documentos_filename = guardar_archivo(documentos_part_file) if documentos_part_file else None
                    clave_par = str(usuario.pk)[::-1]

                    ParticipantesEventos.objects.create(
                        par_eve_participante_fk=participante,
                        par_eve_evento_fk=evento,
                        par_eve_fecha_hora=datetime.utcnow(),
                        par_eve_documentos=documentos_filename,
                        par_eve_or=clave_par,
                        par_eve_clave=clave_par
                    )
                    messages.success(request, "¡Te has preinscrito exitosamente como Participante!")
                else:
                    messages.info(request, "Ya estás registrado como participante en este evento.")

            elif tipo == 'evaluador':
                evaluador, _ = Evaluador.objects.get_or_create(usuario=usuario)

                ya_registrado = EvaluadorEventos.objects.filter(
                    eva_eve_evaluador_fk=evaluador,
                    eva_eve_evento_fk=evento
                ).exists()
                if not ya_registrado:
                    documentos_filename = guardar_archivo(documentos_eval_file) if documentos_eval_file else None
                    clave_eva = str(usuario.pk)[::-1]

                    EvaluadorEventos.objects.create(
                        eva_eve_evaluador_fk=evaluador,
                        eva_eve_evento_fk=evento,
                        eva_eve_fecha_hora=datetime.utcnow(),
                        eva_eve_documentos=documentos_filename,
                        eva_eve_or=clave_eva,
                        eva_eve_clave=clave_eva,
                        eva_estado='PENDIENTE'
                    )
                    messages.success(request, "¡Te has preinscrito exitosamente como Evaluador!")
                else:
                    messages.info(request, "Ya estás registrado como evaluador en este evento.")
            else:
                messages.error(request, "Tipo de inscripción no válido.")
                return redirect('main:lista_eventos')

            # Enviar correo
            asunto = f"Confirmación de registro en {evento.eve_nombre}"
            mensaje = (
                f"Hola {usuario.first_name},\n\n"
                f"Te has preinscrito exitosamente como {tipo.capitalize()} en el evento '{evento.eve_nombre}'.\n"
                f"Tu usuario es: {user_id}\n"
                "Por favor, espera la confirmación.\n"
                "Gracias por participar."
            )
            enviar_correo(usuario.email, asunto, mensaje)

            return redirect('main:lista_eventos')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
            print(form.errors)  #depurador

    else:
        form = RegistroEventoForm()

    return render(request, 'app_registros/formulario_registro.html', {'form': form, 'evento': evento})


def guardar_archivo(fichero):
    filename = fichero.name
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb+') as destination:
        for chunk in fichero.chunks():
            destination.write(chunk)
    return filename


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
