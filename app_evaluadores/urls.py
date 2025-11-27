from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


app_name = 'evaluadores'

urlpatterns = [
    
    path('perfil/', login_required(views.perfil_evaluador, login_url='main:login'), name='perfil_evaluador'),

    path("mis_eventos/", login_required(views.seleccionar_evento_evaluador, login_url='main:login'), name="seleccionar_evento"),

    path('evaluador/<int:eva_id>/evento/<int:evento_id>/panel/', login_required(views.panel_evaluador, login_url='main:login'), name='panel_evaluador'),


# urls.py
    path('evaluadores/seleccionar_evento/', login_required(views.seleccionar_evento, login_url='main:login'), name='seleccionar_evento'),

    path('criterios/<int:evento_id>/', login_required(views.gestionar_criterios, login_url='main:login'), name='gestionar_criterios'),

    path('evaluador/evento/<int:evento_id>/instrumento/', login_required(views.cargar_instrumento, login_url='main:login'), name='cargar_instrumento'),

    path('evaluador/evento/<int:evento_id>/participantes/', login_required(views.lista_participantes, login_url='main:login'), name='lista_participantes'),

    path('evaluador/<str:eva_id>/evento/<int:evento_id>/participante/<str:par_id>/calificar/', login_required(views.calificar_participante, login_url='main:login'), name='calificar_participante'),

    path('evaluador/evento/<int:evento_id>/ranking/', login_required(views.ver_ranking, login_url='main:login'), name='ver_ranking'),


    path('logout/', views.logout_evaluador, name='logout_evaluador'),

    path('evaluador/evento/<int:evento_id>/calificaciones/', login_required(views.ver_calificaciones_evento, login_url='main:login'), name='ver_calificaciones_evento'),

    path('evento/<int:evento_id>/calificaciones/participante/<int:participante_id>/', login_required(views.ver_calificaciones_participante, login_url='main:login'), name='ver_calificaciones_participante'),
    path('evaluador/evento/<int:evento_id>/calificaciones/participante/<int:participante_id>/exportar/', login_required(views.ver_calificaciones_participante, login_url='main:login'), name='exportar_calificaciones_participante'),
    ################# NUEVAS PARA CONSULTAR
    path('verificar/', login_required(views.verificar_evaluador, login_url='main:login'), name='verificar_evaluador'),
    path('modificar/<str:user_id>/<int:evento_id>/', login_required(views.modificar_evaluador, login_url='main:login'), name='modificar_evaluador'),

    path('mi_info/', login_required(views.mi_info, login_url='main:login'), name='mi_info'),

    path('cancelar/<int:evento_id>/<int:user_id>/', login_required(views.cancelar_inscripcion, login_url='main:login'), name='cancelar_inscripcion'),


    path('lista/<int:eve_id>/participantes/', login_required(views.gestionar_inscripciones, login_url='main:login'), name='gestionar_inscripciones'),
    path('evaluador/evento/<int:evento_id>/informacion_tecnica/', login_required(views.cargar_informacion_tecnica, login_url='main:login'), name='cargar_informacion_tecnica'),
    path('<int:evento_id>/consultar-memorias/', login_required(views.consultar_memorias_eva, login_url="main:login"), name='consultar_memorias_eva'),
 
]
