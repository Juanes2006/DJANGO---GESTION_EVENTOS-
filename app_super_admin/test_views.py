import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from app_admin.models import AdministradorEvento
from app_eventos.models import Evento
from app_super_admin.models import Area, Categoria
from django.core import mail

Usuario = get_user_model()

@pytest.mark.django_db
class TestSuperAdminViews:

    @pytest.fixture
    def superuser(self):
        return Usuario.objects.create_user(
            username="superadmin",
            email="super@admin.com",
            password="admin123",
            is_superuser=True,
            is_staff=True
        )

    @pytest.fixture
    def admin_evento(self):
        user = Usuario.objects.create_user(username="admin_evento", email="admin@evento.com", password="123")
        return AdministradorEvento.objects.create(usuario=user, activo=True, aprobado=False)

    # --- PANEL APROBACIONES ---
    def test_panel_aprobaciones_view_lista_admins(self, client, superuser, admin_evento):
        client.force_login(superuser)
        url = reverse("superadmin:panel_aprobaciones")
        response = client.get(url)

        assert response.status_code == 200
        assert "solicitudes" in response.context
        assert admin_evento in response.context["solicitudes"]

    # --- CAMBIAR ESTADO ADMIN ---
    def test_cambiar_estado_admin_toggle(self, client, superuser, admin_evento):
        client.force_login(superuser)
        url = reverse("superadmin:cambiar_estado_admin", args=[admin_evento.pk])

        old_status = admin_evento.activo
        response = client.get(url, follow=True)
        admin_evento.refresh_from_db()

        assert response.status_code == 200
        assert admin_evento.activo is not old_status  # debe cambiar
        messages = list(response.context["messages"])
        assert any("actualizado correctamente" in str(m) for m in messages)

    # --- APROBAR ADMIN ---
    def test_aprobar_admin_envia_correo(self, client, superuser, admin_evento):
        client.force_login(superuser)
        url = reverse("superadmin:aprobar_admin", args=[admin_evento.pk])

        data = {"limite_eventos": 5, "activo": "on"}
        response = client.post(url, data, follow=True)
        admin_evento.refresh_from_db()

        assert response.status_code == 200
        assert admin_evento.aprobado is True
        assert admin_evento.limite_eventos == 5
        assert len(mail.outbox) == 1
        assert "Aprobación como Administrador" in mail.outbox[0].subject

    # --- AGREGAR ÁREA ---
    def test_agregar_area_crea_nueva_area(self, client, superuser):
        client.force_login(superuser)
        url = reverse("super_admin:agregar_area")

        data = {"are_nombre": "Ciencias", "are_descripcion": "Área de investigación"}
        response = client.post(url, data, follow=True)

        assert response.status_code == 200
        assert Area.objects.filter(are_nombre="Ciencias").exists()

    # --- AGREGAR CATEGORÍA ---
    def test_agregar_categoria_asocia_area(self, client, superuser):
        client.force_login(superuser)
        area = Area.objects.create(are_nombre="Ingeniería", are_descripcion="Test")
        url = reverse("super_admin:agregar_categoria")

        data = {
            "cat_nombre": "Software",
            "cat_descripcion": "Desarrollo de sistemas",
            "cat_area_fk": area.pk
        }

        response = client.post(url, data, follow=True)
        assert response.status_code == 200
        assert Categoria.objects.filter(cat_nombre="Software", cat_area_fk=area).exists()
