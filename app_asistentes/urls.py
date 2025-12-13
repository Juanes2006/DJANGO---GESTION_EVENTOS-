from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'asistente'



urlpatterns = [
    path('panel/', login_required(views.panel_asistente, login_url='main:login'), name='panel_asistente'),
    path('ver_memorias_evento/<int:evento_id>/', login_required(views.ver_memorias_evento_asis, login_url='main:login'), name='ver_memorias_evento_asis'),
    path(
    'modificar_asistente/<int:user_id>/<int:evento_id>/',
    login_required(views.modificar_asistente, login_url='main:login'),
    name='modificar_asistente'
)
]
