from django.urls import path
from . import views

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
]
