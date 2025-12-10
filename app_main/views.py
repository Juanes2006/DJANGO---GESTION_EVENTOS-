from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app_eventos.models import Evento
from app_super_admin.models import Categoria, Area
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from app_usuarios.models import Usuario
from app_evaluadores.models import Evaluador
from app_evaluadores.models import Evaluador, EvaluadorEventos  # asegurarte de importar el intermedio si es necesario
from django.contrib.auth.decorators import login_required
##########################################################
#manejo de errores personalizados

from django.utils.deprecation import MiddlewareMixin

class Error500Middleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        return redirect('main:visitante')  # o la vista que prefieras
    
from django.shortcuts import redirect

def handler404(request, exception):
    return redirect('main:login')  # o la ruta que tú quieras

def handler500(request):
    return redirect('main:login')

def handler403(request, exception):
    return redirect('main:login')

def handler400(request, exception):
    return redirect('main:login')




###########################################################################
from django.views.decorators.csrf import csrf_protect

@csrf_protect  
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                request.session['usuario_id'] = user.id
                request.session['rol'] = user.rol

                print("USUARIO EN SESIÓN:", request.session.get('usuario_id'))
                print("ROL DEL USUARIO:", request.session.get('rol'))

               
                rol = user.rol
                redirecciones = {
                    "SUPER_ADMINISTRADOR": "super_admin:super_admin",
                    "ADMINISTRADOR": "admin_evento:ventana",
                    "EVALUADOR": "evaluadores:seleccionar_evento",
                    "PARTICIPANTE": "participantes:panel_participante",
                    "ASISTENTE": "asistente:panel_asistente",
                }

                return redirect(redirecciones.get(rol, "login_view"))



                if rol in redirecciones:
                    return redirect(redirecciones[rol])
                else:
                    messages.error(request, "⛔ Rol desconocido.")
                    return redirect("login_view")
            else:
                messages.error(request, "⛔ Tu cuenta está desactivada.")
        else:
            messages.error(request, "❌ Credenciales incorrectas.")

    return render(request, "app_main/login.html")



def lista_eventos(request):
    eventos = Evento.objects.filter(eve_estado__iexact="activo")
    return render(request, 'app_eventos/lista_eventos.html', {
        'titulo': "Eventos Activos",
        'eventos': eventos
    })

def visitante(request):
    return render(request, 'app_participantes/visitante_web.html')

def eventos_proximos(request):
    eventos = Evento.objects.filter(eve_estado="ACTIVO")
    return render(request, 'app_eventos/lista_eventos.html', {
        'titulo': "Eventos Próximos",
        'eventos': eventos
    })
def buscar_eventos(request):
    eventos = []
    areas = Area.objects.all()

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        fecha_inicio_str = request.POST.get("fecha_inicio", "").strip()
        ciudad = request.POST.get("ciudad", "").strip()
        area = request.POST.get("area", "").strip()

        query = Evento.objects.all()

        if nombre:
            query = query.filter(eve_nombre__icontains=nombre)

        if fecha_inicio_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
                query = query.filter(eve_fecha_inicio__gte=fecha_inicio)
            except ValueError:
                messages.warning(request, "Formato de fecha inválido. Usa AAAA-MM-DD.")

        if ciudad:
            query = query.filter(eve_ciudad__icontains=ciudad)

        if area:
            if Area.objects.filter(are_codigo=area).exists():
                query = query.filter(categorias__cat_area_fk__are_codigo=area).distinct()
            else:
                messages.warning(request, "El área seleccionada no existe.")

        eventos = query

        if eventos.exists():
            messages.success(request, f"{eventos.count()} evento(s) encontrado(s).")
        else:
            messages.info(request, "No se encontraron eventos con esos criterios.")

    return render(request, 'app_participantes/buscar_eventos.html', {
        'eventos': eventos,
        'areas': areas,
    })

def evento_detalle(request, eve_id):
    evento = get_object_or_404(
        Evento.objects.select_related().prefetch_related('categorias'),
        eve_id=eve_id
    )
    return render(request, 'app_participantes/detalle_eventos.html', {
        'evento': evento
    })


