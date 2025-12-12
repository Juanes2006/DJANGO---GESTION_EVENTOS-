from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import os
from .forms import RegistroEventoForm, ProyectoForm
from app_eventos.models import Evento, MemoriaEvento
from app_registros.models import AsistentesEventos
from app_participantes.models import ParticipantesEventos, Participantes
from app_registros.models import Asistentes
from app_evaluadores.models import Evaluador, EvaluadorEventos
from datetime import datetime
from app_admin.models import AdministradorEvento
from django.contrib import messages
from django.core.mail import send_mail
from app_usuarios.models import Usuario
from django.contrib.auth.decorators import login_required

from twilio.rest import Client
from django.conf import settings
from app_eventos.models import Proyecto



#FUNCION PARA ENVIAR SMS


def enviar_sms(destinatario, mensaje):
   
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=destinatario
        )
        return message.sid  # Devuelve el SID como confirmación
    except Exception as e:
        # Puedes loguearlo o manejarlo como desees
        print(f"Error al enviar SMS: {e}")
        return None
    
    

# Función para enviar correo
def enviar_correo(destinatario, asunto, mensaje):
    email_desde = settings.EMAIL_HOST_USER
    destinatarios = [destinatario]
    send_mail(asunto, mensaje, email_desde, destinatarios, fail_silently=False)




from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
import secrets  # para claves seguras

def registrarme_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    proyectos = Proyecto.objects.filter(evento=evento)

    if request.method == 'POST':
        form = RegistroEventoForm(request.POST, request.FILES)
        if form.is_valid():
            tipo = form.cleaned_data['tipo_inscripcion'].lower()

            # 🚨 No confiar en user_id enviado por el cliente
            # Si ya hay autenticación: user_id = request.user.pk
            # Si no: crear siempre uno nuevo
            username = form.cleaned_data['username']
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            telefono = form.cleaned_data['telefono']

            # --- Validaciones duplicados (a nivel de DB también deberían existir unique=True) ---
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, "El nombre de usuario ya está en uso.")
                return redirect(request.path)
            if Usuario.objects.filter(email=correo).exists():
                messages.error(request, "El correo electrónico ya está en uso.")
                return redirect(request.path)
            if Usuario.objects.filter(telefono=telefono).exists():
                messages.error(request, "Este teléfono ya está en uso.")
                return redirect(request.path)

            # --- Crear usuario seguro ---
            usuario = Usuario.objects.create(
                username=username,
                first_name=nombre,
                email=correo,
                telefono=telefono,
                rol=tipo.upper()
            )

            # --- Validar y guardar archivos ---
            soporte_pago_file = request.FILES.get('soporte_pago')
            documentos_part_file = request.FILES.get('documentos_participante')
            documentos_eval_file = request.FILES.get('documentos_evaluador')

            # Clave segura en lugar de pk invertido
            clave_segura = secrets.token_urlsafe(8)

            if tipo == 'asistente':
                asistente, _ = Asistentes.objects.get_or_create(usuario=usuario)

                if not AsistentesEventos.objects.filter(
                    asi_eve_asistente_fk=asistente,
                    asi_eve_evento_fk=evento
                    ).exists():

                    AsistentesEventos.objects.create(
                        asi_eve_asistente_fk=asistente,
                        asi_eve_evento_fk=evento,
                        asi_eve_fecha_hora=timezone.now(),
                        asi_eve_soporte=soporte_pago_file,   
                        asi_eve_estado='Registrado',
                        asi_eve_clave=clave_segura
                    )

                    messages.success(request, "¡Te has preinscrito exitosamente como Asistente!")
                else:
                    messages.info(request, "Ya estás registrado como asistente en este evento.")
                messages.info(request, "Ya estás registrado como asistente en este evento.")

            elif tipo == 'participante':
                participante, _ = Participantes.objects.get_or_create(usuario=usuario)
                if not ParticipantesEventos.objects.filter(
                        par_eve_participante_fk=participante,
                        par_eve_evento_fk=evento).exists():
                    documentos_filename = guardar_archivo(documentos_part_file) if documentos_part_file else None

                    proyecto = None
                    opcion_proyecto = request.POST.get("opcion_proyecto")

                    if opcion_proyecto == "nuevo":
                        proyecto_form = ProyectoForm(request.POST)
                        if proyecto_form.is_valid():
                            proyecto = proyecto_form.save(commit=False)
                            proyecto.creador = usuario
                            proyecto.evento = evento
                            proyecto.save()
                            proyecto.participantes.add(usuario)
                        else:
                            messages.error(request, f"Errores en proyecto: {proyecto_form.errors}")
                    elif opcion_proyecto == "existente":
                        proyecto_id = request.POST.get("proyecto_id")
                        proyecto = Proyecto.objects.filter(id=proyecto_id, evento=evento).first()
                        if proyecto:
                            proyecto.participantes.add(usuario)

                    ParticipantesEventos.objects.create(
                        par_eve_participante_fk=participante,
                        par_eve_evento_fk=evento,
                        par_eve_fecha_hora=timezone.now(),
                        par_eve_documentos=documentos_filename,
                        par_eve_clave=clave_segura,
                        proyecto=proyecto
                    )
                    messages.success(request, "¡Te has preinscrito exitosamente como Participante!")
                else:
                    messages.info(request, "Ya estás registrado como participante en este evento.")

            elif tipo == 'evaluador':
                evaluador, _ = Evaluador.objects.get_or_create(usuario=usuario)
                if not EvaluadorEventos.objects.filter(
                        eva_eve_evaluador_fk=evaluador,
                        eva_eve_evento_fk=evento).exists():
                    documentos_filename = guardar_archivo(documentos_eval_file) if documentos_eval_file else None
                    EvaluadorEventos.objects.create(
                        eva_eve_evaluador_fk=evaluador,
                        eva_eve_evento_fk=evento,
                        eva_eve_fecha_hora=timezone.now(),
                        eva_eve_documentos=documentos_filename,
                        eva_eve_clave=clave_segura,
                        eva_estado='PENDIENTE'
                    )
                    messages.success(request, "¡Te has preinscrito exitosamente como Evaluador!")
                else:
                    messages.info(request, "Ya estás registrado como evaluador en este evento.")
            else:
                messages.error(request, "Tipo de inscripción no válido.")
                return redirect('main:lista_eventos')

            # --- Notificaciones → refactor recomendado a servicio separado ---
            enviar_sms(usuario, evento, tipo, clave_segura)

            return redirect('main:lista_eventos')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = RegistroEventoForm()

    return render(request, 'app_registros/formulario_registro.html',
                  {'form': form, 'evento': evento, 'proyectos': proyectos})


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



