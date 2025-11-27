import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import date

from app_usuarios.models import Usuario
from app_eventos.models import Evento
from app_participantes.models import Participantes, ParticipantesEventos
from app_evaluadores.models import Criterio, Calificacion, Instrumento
from app_admin.models import AdministradorEvento
from app_evaluadores.models import Evaluador as Evaluadores


# ---------- FIXTURES ----------
# ---------- FIXTURES ----------

@pytest.fixture
def usuario(db):
    """Usuario genérico para crear el AdministradorEvento"""
    return Usuario.objects.create_user(
        username="admin_user",
        email="admin@test.com",
        password="12345",
        first_name="Admin",
        last_name="Evento",
        rol="ADMINISTRADOR"
    )


@pytest.fixture
def usuario_participante(db):
    return Usuario.objects.create_user(
        username="juan",
        email="juan@test.com",
        password="12345",
        first_name="Juan",
        last_name="Pérez",
        rol="PARTICIPANTE"
    )


@pytest.fixture
def participante(db, usuario_participante):
    return Participantes.objects.create(usuario=usuario_participante)


@pytest.fixture
def administrador(db, usuario):
    return AdministradorEvento.objects.create(
        usuario=usuario,
        aprobado=True,
        limite_eventos=5,
        activo=True
    )


@pytest.fixture
def evento(db, administrador):
    return Evento.objects.create(
        eve_nombre="Evento Test",
        eve_estado="ACTIVO",
        eve_ciudad="Bogotá",
        eve_fecha_inicio=date.today(),
        eve_fecha_fin=date.today(),
        adm_id=administrador
    )


@pytest.fixture
def inscripcion(db, participante, evento):
    return ParticipantesEventos.objects.create(
        par_eve_participante_fk=participante,
        par_eve_evento_fk=evento,
        par_eve_fecha_hora=timezone.now(),
        par_eve_clave="abc123",
        par_estado="ACEPTADO"
    )

# ---------- TESTS DE VISTAS ----------

@pytest.mark.django_db
def test_panel_participante_autenticado(client, usuario_participante, participante, inscripcion):
    """Debe mostrar el panel del participante autenticado"""
    client.force_login(usuario_participante)
    url = reverse("participantes:panel_participante")
    response = client.get(url)
    assert response.status_code == 200
    assert "panel_participante" in response.templates[0].name


@pytest.mark.django_db
def test_ver_memorias_evento_sin_permiso(client, usuario_participante, evento):
    """Debe redirigir si el participante no está inscrito"""
    client.force_login(usuario_participante)
    url = reverse("participantes:ver_memorias_evento", args=[evento.eve_id])
    response = client.get(url)
    assert response.status_code == 302  # redirige al listado de eventos


@pytest.mark.django_db
def test_ver_memorias_evento_con_permiso(client, usuario_participante, participante, inscripcion):
    """Debe mostrar memorias si está inscrito"""
    client.force_login(usuario_participante)
    url = reverse("participantes:ver_memorias_evento", args=[inscripcion.par_eve_evento_fk.eve_id])
    response = client.get(url)
    assert response.status_code == 200
    assert "memorias_evento" in response.templates[0].name


@pytest.mark.django_db
def test_modificar_participante_get(client, usuario_participante, participante, evento, inscripcion):
    """Debe mostrar el formulario para modificar participante"""
    client.force_login(usuario_participante)
    url = reverse("participantes:modificar_participante", args=[participante.pk, evento.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "modificar_participante" in response.templates[0].name


@pytest.mark.django_db
def test_modificar_participante_post(client, usuario_participante, participante, evento, inscripcion):
    """Debe permitir modificar datos del participante"""
    client.force_login(usuario_participante)
    url = reverse("participantes:modificar_participante", args=[participante.pk, evento.pk])
    data = {"nombre": "Nuevo Nombre", "correo": "nuevo@test.com", "telefono": "987654"}
    response = client.post(url, data)
    assert response.status_code == 302  # redirige tras actualizar
    participante.refresh_from_db()
    assert participante.usuario.email == "juan@test.com"  # usuario no cambia
    assert ParticipantesEventos.objects.filter(par_eve_participante_fk=participante).exists()


@pytest.mark.django_db
def test_mi_info_view(client, usuario_participante, participante, inscripcion):
    """Debe cargar la información del participante"""
    client.force_login(usuario_participante)
    url = reverse("participantes:mi_info")
    response = client.get(url)
    assert response.status_code == 200
    assert "par_informacion" in response.templates[0].name
    
    
@pytest.mark.django_db
def test_ver_instrumento_view(client, usuario_participante, participante, evento):
    client.force_login(usuario_participante)
    ParticipantesEventos.objects.create(
        par_eve_participante_fk=participante,
        par_eve_evento_fk=evento,
        par_eve_fecha_hora=timezone.now(),
        par_eve_clave="clave123",
        par_estado="ACEPTADO"
    )
    Criterio.objects.create(cri_descripcion="Calidad", cri_evento_fk=evento, cri_peso=0.5)
    url = reverse("participantes:ver_instrumento", args=[evento.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "instrumento" in response.templates[0].name


@pytest.mark.django_db
def test_ver_calificaciones_view(client, usuario_participante, participante, evento):
    client.force_login(usuario_participante)
    criterio = Criterio.objects.create(cri_descripcion="Innovación", cri_evento_fk=evento, cri_peso=0.5)
    evaluador = Evaluadores.objects.create(usuario=usuario_participante)

    # ✅ Aseguramos que el participante está inscrito
    ParticipantesEventos.objects.create(
        par_eve_participante_fk=participante,
        par_eve_evento_fk=evento,
        par_eve_fecha_hora=timezone.now(),
        par_eve_clave="clave123",
        par_estado="ACEPTADO"
    )

    Calificacion.objects.create(
        cal_criterio_fk=criterio,
        cal_participante_fk=participante,
        cal_evaluador_fk=evaluador,
        cal_valor=10
    )

    url = reverse("participantes:ver_calificaciones", args=[participante.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "calificaciones" in response.templates[0].name


@pytest.mark.django_db
def test_ranking_participantes_view(client, usuario_participante, participante, evento):
    client.force_login(usuario_participante)

    # ✅ Inscribimos al participante
    ParticipantesEventos.objects.create(
        par_eve_participante_fk=participante,
        par_eve_evento_fk=evento,
        par_eve_fecha_hora=timezone.now(),
        par_eve_clave="clave123",
        par_estado="ACEPTADO"
    )

    Criterio.objects.create(cri_descripcion="Originalidad", cri_evento_fk=evento, cri_peso=0.5)
    url = reverse("participantes:ranking_participantes", args=[evento.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "ranking" in response.templates[0].name



@pytest.mark.django_db
def test_ver_calificaciones_participante_view(client, usuario_participante, participante, evento):
    client.force_login(usuario_participante)
    criterio = Criterio.objects.create(cri_descripcion="Impacto", cri_evento_fk=evento, cri_peso=0.5)
    evaluador = Evaluadores.objects.create(usuario=usuario_participante)
    Calificacion.objects.create(
        cal_criterio_fk=criterio,
        cal_participante_fk=participante,
        cal_evaluador_fk=evaluador,
        cal_valor=9
    )
    url = reverse("participantes:ver_calificaciones_participante", args=[evento.pk, participante.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "calificaciones_participante" in response.templates[0].name
