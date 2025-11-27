# app_admin/tests/test_views.py
import pytest
from django.urls import reverse
from django.test import Client
from app_usuarios.models import Usuario
from app_admin.models import AdministradorEvento, PlantillaCertificado
from app_eventos.models import Evento
from app_evaluadores.models import Criterio
from app_participantes.models import Participante, ParticipantesEventos


from django.contrib.auth import get_user_model
from app_admin.models import Asistentes, AsistentesEventos, PlantillaCertificado, Evento

User = get_user_model()

pytestmark = pytest.mark.django_db


# ---------- HELPERS ----------
def crear_usuario_admin(aprobado=True):
    user = Usuario.objects.create_user(
        email="admin@test.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        password="12345",
        rol="ADMINISTRADOR"
    )
    AdministradorEvento.objects.create(usuario=user, aprobado=aprobado)
    return user


def crear_evento(admin):
    return Evento.objects.create(
        eve_nombre="Evento Test",
        eve_descripcion="Descripción del evento",
        adm_id=AdministradorEvento.objects.get(usuario=admin)
    )


# ---------- TESTS ----------
# ---------- VENTANA ----------

def test_ventana_admin_aprobado_renderiza_correctamente(client):
    user = crear_usuario_admin(aprobado=True)
    client.force_login(user)

    url = reverse("admin_evento:ventana")
    response = client.get(url)

    assert response.status_code == 200
    assert "app_admin/administrador_evento.html" in [t.name for t in response.templates]
    assert "eventos" in response.context


def test_ventana_admin_no_aprobado_retorna_forbidden(client):
    user = crear_usuario_admin(aprobado=False)
    client.force_login(user)
    url = reverse("admin_evento:ventana")
    response = client.get(url)
    assert response.status_code == 403
    
def test_ventana_usuario_con_rol_invalido(client):
    user = Usuario.objects.create_user(
        email="test@test.com",
        username="wrong",
        password="12345",
        rol="PARTICIPANTE"  # ❌ NO ADMINISTRADOR
    )
    client.force_login(user)

    url = reverse("admin_evento:ventana")
    response = client.get(url)

    assert response.status_code == 403

def test_ventana_usuario_con_rol_invalido(client):
    user = Usuario.objects.create_user(
        email="test@test.com",
        username="wrong",
        password="12345",
        rol="PARTICIPANTE"  # ❌ NO ADMINISTRADOR
    )
    client.force_login(user)

    url = reverse("admin_evento:ventana")
    response = client.get(url)

    assert response.status_code == 403

def test_ventana_admin_sin_registro_en_administradorevento(client):
    user = Usuario.objects.create_user(
        email="test2@test.com",
        username="no-admin-reg",
        password="12345",
        rol="ADMINISTRADOR"  # ✅ rol correcto
    )
    client.force_login(user)

    url = reverse("admin_evento:ventana")
    response = client.get(url)

    assert response.status_code == 403
    

# ---------- ----------


def test_gestionar_inscripciones_renderiza_correctamente(client):
    admin = crear_usuario_admin()
    evento = crear_evento(admin)
    client.force_login(admin)

    # Crear un participante
    participante_user = Usuario.objects.create_user(
        email="user@test.com",
        username="user_test",
        password="12345",
        first_name="Test",
        last_name="User"
    )
    participante = Participante.objects.create(usuario=participante_user)

    # Crear relación Participante ↔ Evento
    pe = ParticipantesEventos.objects.create(
        par_eve_evento_fk=evento,
        par_eve_participante_fk=participante,
        par_estado="INSCRITO",
        par_eve_documentos="doc_test.pdf"
    )

    # Crear Plantillas
    plantilla = PlantillaCertificado.objects.create(nombre="Certificado Test")

    url = reverse("admin_evento:gestionar_inscripciones", args=[evento.pk])
    response = client.get(url)

    # Validaciones generales
    assert response.status_code == 200
    assert "app_admin/gestionar_inscripciones.html" in [t.name for t in response.templates]

    # Validaciones de contexto
    assert "evento" in response.context
    assert response.context["evento"] == evento

    assert "plantillas" in response.context
    assert plantilla in response.context["plantillas"]

    assert "participantes" in response.context
    participantes = response.context["participantes"]

    assert len(participantes) == 1
    assert participantes[0]["id"] == participante_user.id
    assert participantes[0]["username"] == "user_test"
    assert participantes[0]["email"] == "user@test.com"
    assert participantes[0]["first_name"] == "Test"
    assert participantes[0]["last_name"] == "User"
    assert participantes[0]["par_estado"] == "INSCRITO"
    assert participantes[0]["par_eve_documentos"] == "doc_test.pdf"




def test_gestionar_inscripcion_asis_renderiza_correctamente(client):
    # Crear usuario administrador
    admin = crear_usuario_admin()

    # Crear evento
    evento = crear_evento(admin)

    # Crear usuario asistente (normal)
    usuario_asistente = User.objects.create_user(
        username="usuario_asistente",
        email="asistente@test.com",
        password="test1234"
    )

    # Crear instancia de Asistentes
    asistente = Asistentes.objects.create(usuario=usuario_asistente)

    # Crear relación asistente - evento
    AsistentesEventos.objects.create(
        asi_eve_evento_fk=evento,
        asi_eve_asistente_fk=asistente,
        asi_eve_estado="pendiente",
        asi_eve_soporte="documento.pdf"
    )

    # Crear al menos una plantilla
    PlantillaCertificado.objects.create(nombre="Plantilla Test")

    # Loguear admin
    client.force_login(admin)

    # Consumir vista
    url = reverse("admin_evento:gestionar_inscripcion_asis", args=[evento.pk])
    response = client.get(url)

    # Validaciones
    assert response.status_code == 200
    assert "app_admin/gestionar_inscripciones_asis.html" in [t.name for t in response.templates]

    # Verificar contexto
    assert "evento" in response.context
    assert response.context["evento"] == evento

    assert "asistentes" in response.context
    assert len(response.context["asistentes"]) == 1
    assert response.context["asistentes"][0]["username"] == usuario_asistente.username

    assert "plantillas" in response.context
    assert response.context["plantillas"].count() >= 1


def test_gestionar_evaluadores_renderiza_correctamente(client):
    admin = crear_usuario_admin()
    evento = crear_evento(admin)
    client.force_login(admin)
    url = reverse("admin_evento:gestionar_evaluadores", args=[evento.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "app_admin/gestionar_evaluadores.html" in [t.name for t in response.templates]


def test_toggle_inscripcion_alterna_correctamente(client):
    admin = crear_usuario_admin()
    evento = crear_evento(admin)
    client.force_login(admin)
    url = reverse("admin_evento:toggle_inscripcion", args=[evento.pk, "participantes"])
    client.get(url)
    evento.refresh_from_db()
    assert evento.inscripciones_participantes_abiertas is False


def test_gestionar_criterios_admin_crear_criterio_valido(client):
    admin = crear_usuario_admin()
    evento = crear_evento(admin)
    client.force_login(admin)
    url = reverse("admin_evento:gestionar_criterios_admin", args=[evento.pk])
    data = {"accion": "crear", "descripcion": "Criterio 1", "peso": "40"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert Criterio.objects.filter(cri_evento_fk=evento, cri_descripcion="Criterio 1").exists()


def test_gestionar_criterios_admin_rechaza_peso_invalido(client):
    admin = crear_usuario_admin()
    evento = crear_evento(admin)
    client.force_login(admin)
    url = reverse("admin_evento:gestionar_criterios_admin", args=[evento.pk])
    data = {"accion": "crear", "descripcion": "Criterio Invalido", "peso": "abc"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert not Criterio.objects.filter(cri_evento_fk=evento, cri_descripcion="Criterio Invalido").exists()


def test_actualizar_estado_metodo_get_no_permitido(client):
    admin = crear_usuario_admin()
    client.force_login(admin)
    url = reverse("admin_evento:actualizar_estado")
    response = client.get(url)
    assert response.status_code == 302  # redirección por error de método


def test_actualizar_estado_faltan_datos(client):
    admin = crear_usuario_admin()
    client.force_login(admin)
    url = reverse("admin_evento:actualizar_estado")
    response = client.post(url, {})
    assert response.status_code == 302  # redirige con mensaje de error

def test_ventana_usuario_no_autenticado(client):
    url = reverse("admin_evento:ventana")
    response = client.get(url)

    # login_required should redirect to login
    assert response.status_code == 302
    assert "/login" in response.url.lower()
