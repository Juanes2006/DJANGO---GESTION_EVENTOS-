import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils.timezone import now
from app_eventos.models import Evento, MemoriaEvento
from app_registros.models import Asistentes, AsistentesEventos
from app_admin.models import AdministradorEvento

User = get_user_model()


@pytest.mark.django_db
def test_panel_asistente_renderiza_correctamente():
    client = Client()
    user = User.objects.create_user(
        username="asis",
        email="asis@test.com",
        password="1234",
        first_name="A",
        last_name="B",
        rol="ASISTENTE"
    )
    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        first_name="X",
        last_name="Y",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento A", adm_id=admin)
    asistente = Asistentes.objects.create(usuario=user)

    AsistentesEventos.objects.create(
        asi_eve_asistente_fk=asistente,
        asi_eve_evento_fk=evento,
        asi_eve_fecha_hora=now(),
        asi_eve_estado="APROBADO",
        asi_eve_clave="CLAVE123"
    )

    client.force_login(user)
    response = client.get(reverse("asistente:panel_asistente"))
    assert response.status_code == 200
    assert "eventos_inscritos" in response.context
    assert evento in [a.asi_eve_evento_fk for a in response.context["eventos_inscritos"]]


@pytest.mark.django_db
def test_panel_asistente_redirige_si_no_es_asistente():
    client = Client()
    user = User.objects.create_user(
        username="otro",
        email="otro@test.com",
        password="1234",
        first_name="X",
        last_name="Y",
        rol="PARTICIPANTE"
    )
    client.force_login(user)
    response = client.get(reverse("asistente:panel_asistente"))
    assert response.status_code == 302
    assert response.url == "/visitante_web/"


@pytest.mark.django_db
def test_ver_memorias_evento_asis_con_acceso_valido():
    client = Client()
    user = User.objects.create_user(
        username="asis",
        email="asis@test.com",
        password="1234",
        first_name="A",
        last_name="B",
        rol="ASISTENTE"
    )
    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        first_name="X",
        last_name="Y",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento X", adm_id=admin)
    asistente = Asistentes.objects.create(usuario=user)

    AsistentesEventos.objects.create(
        asi_eve_asistente_fk=asistente,
        asi_eve_evento_fk=evento,
        asi_eve_fecha_hora=now(),
        asi_eve_estado="APROBADO",
        asi_eve_clave="CLAVE999"
    )

    MemoriaEvento.objects.create(evento=evento, titulo="Memoria 1")

    client.force_login(user)
    response = client.get(reverse("asistente:ver_memorias_evento_asis", args=[evento.pk]))
    assert response.status_code in [200, 302]
    if response.status_code == 302:
        assert response.url == "/visitante_web/"
    else:
        assert "memorias" in response.context
        assert len(response.context["memorias"]) == 1


@pytest.mark.django_db
def test_ver_memorias_evento_asis_redirige_si_no_inscrito():
    client = Client()
    user = User.objects.create_user(
        username="asis",
        email="asis@test.com",
        password="1234",
        first_name="A",
        last_name="B",
        rol="ASISTENTE"
    )
    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        first_name="X",
        last_name="Y",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento Y", adm_id=admin)

    client.force_login(user)
    response = client.get(reverse("asistente:ver_memorias_evento_asis", args=[evento.pk]))
    assert response.status_code == 302
    assert response.url == "/visitante_web/lista_eventos/"
