from django.urls import path
from . import views

app_name = 'participantes'

urlpatterns = [
    path('verificar/', views.verificar_participante, name='verificar_participante'),
    path('modificar/<str:user_id>/<int:evento_id>/', views.modificar_participante, name='modificar_participante'),
    path('panel/', views.panel_participante, name='panel_participante'),
    path('mi_info/', views.mi_info, name='mi_info'),
    path('instrumento/<int:evento_id>/', views.ver_instrumento, name='ver_instrumento'),
    path('calificaciones/<str:participante_id>/', views.ver_calificaciones, name='ver_calificaciones'),
    path('ranking/<int:evento_id>/', views.ranking_participantes, name='ranking_participantes'),
    path('evento/<int:evento_id>/calificaciones/participante/<int:participante_id>/', views.ver_calificaciones_participante, name='ver_calificaciones_participante'),
]
