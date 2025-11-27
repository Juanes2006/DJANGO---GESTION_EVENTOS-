# app_eventos/test_views.py
import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from app_eventos import views


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.is_authenticated = True
    return user


def add_middleware(request):
    setattr(request, "session", {})
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


# ---------- CREAR EVENTO ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.AdministradorEvento")
@patch("app_eventos.views.Evento")
@patch("app_eventos.views.Categoria")
def test_crear_evento_post(mock_categoria, mock_evento, mock_admin, mock_redirect, rf, mock_user):
    # No usar multipart/form-data, solo simular POST normal
    request = rf.post("/crear-evento/", data={"nombre": "Evento Test"})
    request.user = mock_user
    add_middleware(request)

    # Mockear directamente request.FILES sin activar parser interno
    type(request).FILES = property(lambda self: {"imagen": None, "archivo_programacion": None})

    mock_admin.objects.get.return_value = MagicMock()
    mock_evento.objects.create.return_value = MagicMock(pk=1, eve_nombre="Evento Test")
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.crear_evento(request)
    assert response.status_code == 302
    mock_evento.objects.create.assert_called_once()


# ---------- EDITAR EVENTO ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.get_object_or_404")
def test_editar_evento_post(mock_get, mock_redirect, rf, mock_user):
    evento_mock = MagicMock()
    mock_get.return_value = evento_mock
    request = rf.post("/editar/1/", data={"nombre": "Nuevo"})
    request.user = mock_user
    add_middleware(request)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.editar_evento(request, pk=1)
    assert response.status_code == 302
    assert evento_mock.save.called


# ---------- CANCELAR EVENTO ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.get_object_or_404")
def test_cancelar_evento(mock_get, mock_redirect, rf):
    evento = MagicMock(eve_nombre="E1")
    mock_get.return_value = evento
    request = rf.get("/cancelar/1/")
    add_middleware(request)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.cancelar_evento(request, 1)
    assert response.status_code == 302
    assert evento.save.called


# ---------- ACTIVAR EVENTO ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.get_object_or_404")
def test_activar_evento(mock_get, mock_redirect, rf):
    evento = MagicMock(eve_nombre="E2")
    mock_get.return_value = evento
    request = rf.get("/activar/1/")
    add_middleware(request)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.activar_evento(request, 1)
    assert response.status_code == 302
    assert evento.save.called


# ---------- DESACTIVAR EVENTO ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.get_object_or_404")
def test_desactivar_evento(mock_get, mock_redirect, rf):
    evento = MagicMock(eve_nombre="E3")
    mock_get.return_value = evento
    request = rf.get("/desactivar/1/")
    add_middleware(request)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.desactivar_evento(request, 1)
    assert response.status_code == 302
    assert evento.save.called


# ---------- ELIMINAR EVENTO ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.get_object_or_404")
def test_eliminar_evento(mock_get, mock_redirect, rf):
    evento = MagicMock(eve_nombre="E4")
    mock_get.return_value = evento
    request = rf.get("/eliminar/1/")
    add_middleware(request)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.eliminar_evento(request, 1)
    assert response.status_code == 302
    assert evento.delete.called


# ---------- SUBIR MEMORIA ----------
@patch("app_eventos.views.render")
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.MemoriaEvento")
@patch("app_eventos.views.get_object_or_404")
def test_subir_memoria_evento(mock_get, mock_memoria, mock_redirect, mock_render, rf):
    evento = MagicMock()
    mock_get.return_value = evento
    request = rf.post("/subir/1/", data={"titulo": "Memoria"})
    add_middleware(request)

    # ✅ Mock para request.FILES (sin usar setter)
    mock_files = MagicMock()
    mock_files.getlist.return_value = []  # Simula lista vacía de archivos
    type(request).FILES = property(lambda self: mock_files)

    mock_render.return_value = MagicMock(status_code=200)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.subir_memoria_evento(request, 1)
    assert response.status_code in (200, 302)


# ---------- CONSULTAR MEMORIAS ----------
@patch("app_eventos.views.render")
@patch("app_eventos.views.MemoriaEvento")
@patch("app_eventos.views.get_object_or_404")
def test_consultar_memorias(mock_get, mock_memoria, mock_render, rf):
    mock_get.return_value = MagicMock()
    mock_memoria.objects.filter.return_value = []
    mock_render.return_value = MagicMock(status_code=200)

    response = views.consultar_memorias(rf.get("/consultar/1/"), 1)
    assert response.status_code == 200


# ---------- ELIMINAR MEMORIA ----------
@patch("app_eventos.views.redirect")
@patch("app_eventos.views.MemoriaEvento")
def test_eliminar_memoria(mock_memoria, mock_redirect, rf):
    mock_memoria.objects.filter.return_value.delete.return_value = (1, {})
    request = rf.post("/eliminar-memoria/1/", data={"evento_id": "1"})
    add_middleware(request)
    mock_redirect.return_value = MagicMock(status_code=302)

    response = views.eliminar_memoria(request, 1)
    assert response.status_code == 302
    assert mock_memoria.objects.filter.called
