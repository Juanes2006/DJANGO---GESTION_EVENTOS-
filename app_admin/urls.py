from django.urls import path
from . import views

app_name = 'admin_evento'


urlpatterns = [
    path('', views.ventana, name='ventana'),
    
    path('evento/<int:evento_id>/toggle/<str:tipo>/', views.toggle_inscripcion, name='toggle_inscripcion'),
    
    path('evento/<int:evento_id>/calificaciones/', views.ver_calificaciones_evento, name='ver_calificaciones_evento'),

    path('evento/<int:eve_id>/participantes/', views.gestionar_inscripciones, name='gestionar_inscripciones'),
    
    path('evento/<int:eve_id>/asistentes/', views.gestionar_inscripcion_asis, name='gestionar_inscripcion_asis'),
    
    path('actualizar_estado/', views.actualizar_estado, name='actualizar_estado'),
    
    
    

    path('criterios/<int:evento_id>/', views.gestionar_criterios_admin, name='gestionar_criterios_admin'),
    
    path('cargar_instrumento/<int:evento_id>/', views.cargar_instrumento_admin, name='cargar_instrumento_admin'),
    
    path('gestionar_evaluadores/<int:evento_id>/', views.gestionar_evaluadores, name='gestionar_evaluadores'),
        
    path('estadisticas/', views.ver_estadisticas, name='ver_estadisticas'),
    
    path('ranking/<int:evento_id>/', views.ver_ranking_admin, name='ver_ranking_admin'),
    
    path('ranking/<int:evento_id>/descargar/', views.descargar_ranking, name='descargar_ranking'),
    ######################3
    
    ### certificados de participacion 
     path('certificados/asistentes/<int:evento_id>/', views.enviar_certificados_asistentes, name='enviar_certificados_asistentes'),
    path('certificados/participantes/<int:evento_id>/', views.enviar_certificados_participantes, name='enviar_certificados_participantes'),
    path('certificados/evaluadores/<int:evento_id>/', views.enviar_certificados_evaluadores, name='enviar_certificados_evaluadores'),

    #  individual
    path('certificado/asistente/<int:evento_id>/<int:usuario_id>/', views.enviar_certificado_asistente_individual, name='enviar_certificado_asistente_individual'),
    path('certificado/participante/<int:evento_id>/<int:usuario_id>/', views.enviar_certificado_participante_individual, name='enviar_certificado_participante_individual'),
    path('certificado/evaluador/<int:evento_id>/<int:usuario_id>/', views.enviar_certificado_evaluador_individual, name='enviar_certificado_evaluador_individual'),
    
    ### notificaciones
    path('notificar/<int:evento_id>/', views.notificar_evento, name='notificar_evento'),
    
    
    ###### certificados casos de edicion
    path('plantillas/crear/', views.crear_plantilla_certificado, name='crear_plantilla_certificado'),

    path('plantillas/', views.listar_plantillas_certificado, name='listar_plantillas_certificado'),

    path('plantilla/<int:plantilla_id>/editar/', views.editar_plantilla_certificado, name='editar_plantilla'),
    path('plantilla/<int:plantilla_id>/preview/', views.previsualizar_certificado, name='previsualizar_certificado'),
    path('plantilla/<int:plantilla_id>/eliminar/', views.eliminar_plantilla, name='eliminar_plantilla'),
    path('evento/<int:evento_id>/seleccionar-plantilla/<str:rol>/', views.seleccionar_plantilla_envio, name='seleccionar_plantilla_envio'),

    
]
