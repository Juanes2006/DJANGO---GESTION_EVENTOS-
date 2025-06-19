from django.urls import path
from . import views

app_name = 'evaluadores'

urlpatterns = [
    path("mis_eventos/", views.seleccionar_evento_evaluador, name="seleccionar_evento"),

    
    path('evaluador/<int:eva_id>/evento/<int:evento_id>/panel/', views.panel_evaluador, name='panel_evaluador'),


# urls.py
    path('evaluadores/seleccionar_evento/', views.seleccionar_evento, name='seleccionar_evento'),

    path('criterios/<int:evento_id>/', views.gestionar_criterios, name='gestionar_criterios'),

    path('evaluador/evento/<int:evento_id>/instrumento/', views.cargar_instrumento, name='cargar_instrumento'),

    path('evaluador/evento/<int:evento_id>/participantes/', views.lista_participantes, name='lista_participantes'),

    path('evaluador/<str:eva_id>/evento/<int:evento_id>/participante/<str:par_id>/calificar/', views.calificar_participante, name='calificar_participante'),

    path('evaluador/evento/<int:evento_id>/ranking/', views.ver_ranking, name='ver_ranking'),


    path('logout/', views.logout_evaluador, name='logout_evaluador'),

    path('evaluador/evento/<int:evento_id>/calificaciones/', views.ver_calificaciones_evento, name='ver_calificaciones_evento'),

    path('evento/<int:evento_id>/calificaciones/participante/<int:participante_id>/', views.ver_calificaciones_participante, name='ver_calificaciones_participante'),
    
    ################# NUEVAS PARA CONSULTAR
    
    path('verificar/', views.verificar_evaluador, name='verificar_evaluador'),
    path('modificar/<str:user_id>/<int:evento_id>/', views.modificar_evaluador, name='modificar_evaluador'),

    path('mi_info/', views.mi_info, name='mi_info'),
    
    
    path('cancelar/<int:evento_id>/<int:user_id>/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
    
    
    path('lista/<int:eve_id>/participantes/', views.gestionar_inscripciones, name='gestionar_inscripciones'),
    path('evaluador/evento/<int:evento_id>/informacion_tecnica/', views.cargar_informacion_tecnica, name='cargar_informacion_tecnica'),

]
