from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


app_name = 'participantes'

urlpatterns = [
    path('modificar/<str:user_id>/<int:evento_id>/', login_required(views.modificar_participante, login_url='main:login'), name='modificar_participante'),
    path('panel/', login_required(views.panel_participante, login_url='main:login'), name='panel_participante'),
    path('mi_info/', login_required(views.mi_info, login_url='main:login'), name='mi_info'),
    path('instrumento/<int:evento_id>/', login_required(views.ver_instrumento, login_url='main:login'), name='ver_instrumento'),
    path('calificaciones/<str:participante_id>/', login_required(views.ver_calificaciones, login_url='main:login'), name='ver_calificaciones'),
    path('ranking/<int:evento_id>/', login_required(views.ranking_participantes, login_url='main:login'), name='ranking_participantes'),
    path('evento/<int:evento_id>/calificaciones/participante/<int:participante_id>/', login_required(views.ver_calificaciones_participante, login_url='main:login'), name='ver_calificaciones_participante'),
    path('evento/<int:evento_id>/consultar-memorias/', login_required(views.ver_memorias_evento), name='ver_memorias_evento'),



]
