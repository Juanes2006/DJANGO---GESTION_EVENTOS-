import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
from app_eventos.models import Evento, AdministradorEvento
from app_registros.models import Asistentes, AsistentesEventos
from app_participantes.models import Participantes, ParticipantesEventos
from app_evaluadores.models import Evaluador, EvaluadorEventos
from app_usuarios.models import Usuario


@pytest.mark.django_db
class TestRegistroEvento:

    @pytest.fixture
    def setup_evento(self):
        admin_user = Usuario.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="admin123"
        )
        admin_evento = AdministradorEvento.objects.create(usuario=admin_user)
        evento = Evento.objects.create(
            eve_nombre="Evento Test",
            eve_estado="Activo",
            adm_id=admin_evento
        )
        return evento

    @pytest.fixture
    def archivo_falso(self):
        return SimpleUploadedFile("soporte.pdf", b"contenido", content_type="application/pdf")

    def mock_form(self, data):
        """Crea un formulario simulado con cleaned_data y is_valid()=True"""
        form_mock = MagicMock()
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = data
        return form_mock

    @patch("app_registros.views.enviar_sms")
    @patch("app_registros.views.enviar_correo")
    def test_registro_asistente_exitoso(self, mock_correo, mock_sms, client, setup_evento, archivo_falso):
        evento = setup_evento
        url = reverse("registros:registrarme_evento", args=[evento.pk])

        data = {
            "tipo_inscripcion": "asistente",
            "username": "user_asist",
            "nombre": "Asistente Uno",
            "correo": "asistente@test.com",
            "telefono": "1234567890",
        }

        mock_form_instance = self.mock_form(data)

        with patch("app_registros.views.RegistroEventoForm", return_value=mock_form_instance):
            response = client.post(url, data, follow=True)

        assert response.status_code in [200, 302]
        assert Usuario.objects.filter(username="user_asist").exists()
        assert Asistentes.objects.exists()
        assert AsistentesEventos.objects.exists()

    @patch("app_registros.views.enviar_sms")
    def test_registro_participante_exitoso(self, mock_sms, client, setup_evento):
        evento = setup_evento
        url = reverse("registros:registrarme_evento", args=[evento.pk])

        data = {
            "tipo_inscripcion": "participante",
            "username": "user_part",
            "nombre": "Participante Uno",
            "correo": "part@test.com",
            "telefono": "222333444",
            "opcion_proyecto": "nuevo",
        }

        mock_form_instance = self.mock_form(data)

        with patch("app_registros.views.RegistroEventoForm", return_value=mock_form_instance):
            response = client.post(url, data, follow=True)

        assert response.status_code in [200, 302]
        assert Usuario.objects.filter(username="user_part").exists()
        assert Participantes.objects.exists()
        assert ParticipantesEventos.objects.exists()

    @patch("app_registros.views.enviar_sms")
    def test_registro_evaluador_exitoso(self, mock_sms, client, setup_evento):
        evento = setup_evento
        url = reverse("registros:registrarme_evento", args=[evento.pk])

        data = {
            "tipo_inscripcion": "evaluador",
            "username": "user_eval",
            "nombre": "Evaluador Uno",
            "correo": "eval@test.com",
            "telefono": "555666777",
        }

        mock_form_instance = self.mock_form(data)

        with patch("app_registros.views.RegistroEventoForm", return_value=mock_form_instance):
            response = client.post(url, data, follow=True)

        assert response.status_code in [200, 302]
        assert Usuario.objects.filter(username="user_eval").exists()
        assert Evaluador.objects.exists()
        assert EvaluadorEventos.objects.exists()

    @patch("app_registros.views.enviar_correo")
    def test_cancelar_inscripcion_elimina_registro(self, mock_correo, client, setup_evento):
        evento = setup_evento
        usuario = Usuario.objects.create_user(username="asistente2", email="asistente2@test.com", password="123")
        asistente = Asistentes.objects.create(usuario=usuario)
        AsistentesEventos.objects.create(
            asi_eve_asistente_fk=asistente,
            asi_eve_evento_fk=evento,
            asi_eve_fecha_hora=timezone.now(),
            asi_eve_estado="Registrado",
            asi_eve_clave="ABC123"
        )

        # Si tu modelo Asistentes no tiene campo 'asi_id', usa 'pk' directamente
        url = reverse("registros:cancelar_inscripcion", args=[evento.pk, asistente.pk])
        response = client.get(url, follow=True)

        assert response.status_code in [200, 302]
        assert not Asistentes.objects.exists()
        assert not AsistentesEventos.objects.exists()
        mock_correo.assert_called_once()
