import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from app_eventos.models import Evento, AdministradorEvento
from app_participantes.models import Participantes, ParticipantesEventos

User = get_user_model()

@pytest.mark.django_db
class TestQRViews:
    @pytest.fixture
    def setup_data(self, client):
        # Crear usuario base
        user = User.objects.create_user(
            username="usuario_test",
            email="usuario@test.com",
            password="12345"
        )

        # Crear administrador del evento
        admin_user = User.objects.create_user(
            username="admin_evento",
            email="admin@test.com",
            password="admin123"
        )
        admin_evento = AdministradorEvento.objects.create(usuario=admin_user)

        # Crear evento
        evento = Evento.objects.create(
            eve_nombre="Evento Prueba",
            eve_descripcion="Evento de prueba para QR",
            eve_estado="Activo",
            adm_id=admin_evento
        )

        # Crear participante vinculado
        participante = Participantes.objects.create(usuario=user)

        # Relación evento-participante
        ParticipantesEventos.objects.create(
            par_eve_participante_fk=participante,
            par_eve_evento_fk=evento,
            par_estado="ACEPTADO",
            par_eve_clave="CLV123",
            par_eve_fecha_hora=timezone.now()
        )

        # Autenticar usuario directamente
        client.force_login(user)

        return {"client": client, "user": user, "evento": evento, "participante": participante}

    def test_consulta_qr_renderiza_eventos(self, setup_data):
        client = setup_data["client"]
        url = reverse("qr:consulta_qr")
        response = client.get(url)
        assert response.status_code == 200
        assert b"Evento Prueba" in response.content

    def test_consulta_qr_redirige_a_mostrar_qr(self, setup_data):
        client = setup_data["client"]
        evento = setup_data["evento"]
        participante = setup_data["participante"]
        url = reverse("qr:consulta_qr")
        response = client.post(url, {"event_id": evento.pk})
        assert response.status_code == 302
        assert reverse("qr:mostrar_qr", args=[evento.pk, participante.pk]) in response.url

    def test_mostrar_qr_retorna_html_con_qr(self, setup_data):
        client = setup_data["client"]
        evento = setup_data["evento"]
        participante = setup_data["participante"]
        url = reverse("qr:mostrar_qr", args=[evento.pk, participante.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"data:image/png" in response.content  # QR generado correctamente

    def test_descargar_qr_descarga_png(self, setup_data):
        client = setup_data["client"]
        evento = setup_data["evento"]
        participante = setup_data["participante"]
        url = reverse("qr:descargar_qr", args=[evento.pk, participante.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
