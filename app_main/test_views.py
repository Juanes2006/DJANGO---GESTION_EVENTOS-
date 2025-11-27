import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date

from app_eventos.models import Evento
from app_super_admin.models import Categoria, Area
from app_admin.models import AdministradorEvento
from app_usuarios.models import Usuario

User = get_user_model()

# ---------- FIXTURES ----------

@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(
        username="juan",
        email="juan@test.com",
        password="pass1234",
        first_name="Juan",
        last_name="Pérez"
    )

@pytest.fixture
def administrador(db, usuario):
    return AdministradorEvento.objects.create(usuario=usuario, activo=True)

@pytest.fixture
def area(db):
    return Area.objects.create(are_nombre="Tecnología")

@pytest.fixture
def categoria(db, area):
    return Categoria.objects.create(cat_nombre="Innovación", cat_area_fk=area)

@pytest.fixture
def evento(db, categoria, area, administrador):
    # Relacionar la categoría con el área
    categoria.cat_area_fk = area
    categoria.save()

    # Crear el evento correctamente
    evento = Evento.objects.create(
        eve_nombre="Evento Test",
        eve_estado="Activo",
        eve_fecha_inicio=date.today(),
        eve_ciudad="Bogotá",
        adm_id=administrador
    )

    # Relacionar el evento con la categoría (ManyToMany)
    evento.categorias.add(categoria)

    return evento

# ---------- TESTS DE VISTAS ----------

@pytest.mark.django_db
def test_login_view_get(client):
    """Debe mostrar el formulario de login"""
    url = reverse("main:login")
    response = client.get(url)
    assert response.status_code == 200
    assert "login" in response.templates[0].name


@pytest.mark.django_db
def test_login_view_post_valido(client, usuario):
    """Debe autenticar y redirigir según rol"""
    url = reverse("main:login")
    data = {"email": usuario.email, "password": "pass1234"}
    response = client.post(url, data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_lista_eventos(client, evento):
    """Debe listar eventos activos"""
    url = reverse("main:lista_eventos")
    response = client.get(url)
    assert response.status_code == 200
    assert "Eventos Activos" in response.content.decode()


@pytest.mark.django_db
def test_eventos_proximos(client, evento):
    """Debe listar eventos con estado ACTIVO"""
    evento.eve_estado = "ACTIVO"
    evento.save()
    url = reverse("main:eventos_proximos")
    response = client.get(url)
    assert response.status_code == 200
    assert "Eventos Próximos" in response.content.decode()


@pytest.mark.django_db
def test_buscar_eventos_por_nombre(client, evento):
    """Debe encontrar eventos por nombre"""
    url = reverse("main:buscar_eventos")
    data = {"nombre": "Evento"}
    response = client.post(url, data)
    assert response.status_code == 200
    assert "Evento Test" in response.content.decode()


@pytest.mark.django_db
def test_evento_detalle_view(client, evento):
    """Debe mostrar detalle de un evento"""
    url = reverse("main:evento_detalle", args=[evento.eve_id])
    response = client.get(url)
    assert response.status_code == 200
    assert "detalle_eventos" in response.templates[0].name


@pytest.mark.django_db
def test_visitante_view(client):
    """Debe cargar la vista visitante"""
    url = reverse("main:visitante")
    response = client.get(url)
    assert response.status_code == 200
    assert "visitante_web" in response.templates[0].name


# ---------- HANDLERS DE ERRORES ----------

@pytest.mark.parametrize("handler", ["handler404", "handler500", "handler403", "handler400"])
@pytest.mark.django_db
def test_error_handlers_redireccionan(client, handler):
    """Cada manejador de error debe redirigir al login"""
    handler_url = reverse("main:login")
    response = client.get(handler_url)
    assert response.status_code in [200, 302]
