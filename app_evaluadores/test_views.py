import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils.timezone import now
from app_eventos.models import Evento
from app_evaluadores.models import Evaluador, Instrumento, InformacionTecnica
from app_admin.models import AdministradorEvento

User = get_user_model()


@pytest.mark.django_db
def test_perfil_evaluador_renderiza_correctamente():
    client = Client()
    user = User.objects.create_user(
        username="eva",
        email="eva@test.com",
        password="1234",
        rol="EVALUADOR"
    )
    Evaluador.objects.create(usuario=user)
    client.force_login(user)
    print(user.rol)


    response = client.get(reverse("evaluadores:perfil_evaluador"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_perfil_evaluador_redirige_si_no_es_evaluador():
    client = Client()
    user = User.objects.create_user(
        username="otro",
        email="otro@test.com",
        password="1234",
        rol="ASISTENTE"
    )
    client.force_login(user)

    response = client.get(reverse("evaluadores:perfil_evaluador"))
    assert response.status_code == 302
    assert "/visitante_web/lista_eventos/" in response.url


@pytest.mark.django_db
def test_cargar_instrumento_crea_nuevo_instrumento():
    client = Client()
    user = User.objects.create_user(
        username="eva",
        email="eva@test.com",
        password="1234",
        rol="EVALUADOR"
    )
    client.force_login(user)

    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento 1", adm_id=admin)

    response = client.post(
        reverse("evaluadores:cargar_instrumento", args=[evento.pk]),
        {"tipo": "PDF", "descripcion": "Nuevo instrumento"}
    )

    assert response.status_code == 302
    assert Instrumento.objects.filter(inst_evento_fk=evento).exists()


@pytest.mark.django_db
def test_cargar_instrumento_actualiza_existente():
    client = Client()
    user = User.objects.create_user(
        username="eva",
        email="eva@test.com",
        password="1234",
        rol="EVALUADOR"
    )
    client.force_login(user)

    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento 2", adm_id=admin)

    inst = Instrumento.objects.create(
        inst_evento_fk=evento,
        inst_tipo="PDF",
        inst_descripcion="Antiguo"
    )

    response = client.post(
        reverse("evaluadores:cargar_instrumento", args=[evento.pk]),
        {"tipo": "XLS", "descripcion": "Actualizado"}
    )

    inst.refresh_from_db()
    assert response.status_code == 302
    assert inst.inst_tipo == "XLS"
    assert inst.inst_descripcion == "Actualizado"


@pytest.mark.django_db
def test_cargar_informacion_tecnica_crea_y_actualiza():
    client = Client()
    user = User.objects.create_user(
        username="eva",
        email="eva@test.com",
        password="1234",
        rol="EVALUADOR"
    )
    client.force_login(user)

    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento 3", adm_id=admin)

    # Crear
    response = client.post(
        reverse("evaluadores:cargar_informacion_tecnica", args=[evento.pk]),
        {"nombre": "Folleto", "descripcion": "Detalles técnicos"}
    )
    assert response.status_code == 302
    info = InformacionTecnica.objects.get(inf_evento_fk=evento)
    assert info.inf_nombre == "Folleto"

    # Actualizar
    response = client.post(
        reverse("evaluadores:cargar_informacion_tecnica", args=[evento.pk]),
        {"nombre": "Actualizado", "descripcion": "Nueva descripción"}
    )
    info.refresh_from_db()
    assert info.inf_nombre == "Actualizado"


@pytest.mark.django_db
def test_ver_ranking_renderiza_correctamente():
    client = Client()
    user = User.objects.create_user(
        username="eva",
        email="eva@test.com",
        password="1234",
        rol="EVALUADOR"
    )
    Evaluador.objects.create(usuario=user)
    client.force_login(user)

    admin_user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="1234",
        rol="ADMINISTRADOR"
    )
    admin = AdministradorEvento.objects.create(usuario=admin_user, aprobado=True)
    evento = Evento.objects.create(eve_nombre="Evento Ranking", adm_id=admin)

    response = client.get(reverse("evaluadores:ver_ranking", args=[evento.pk]))
    assert response.status_code == 200
    assert "ranking" in response.context
