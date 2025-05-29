from django.urls import path
from . import views
app_name = 'main'
urlpatterns = [
    path('visitante_web/lista_eventos/', views.lista_eventos, name='lista_eventos'),
    path('', views.visitante, name='visitante'),
    path('visitante_web/', views.visitante, name='visitante'),
    path('eventos_proximos/', views.eventos_proximos, name='eventos_proximos'),
    path('visitante_web/buscar_eventos/', views.buscar_eventos, name='buscar_eventos'),
    path('evento_detalle/<int:eve_id>/', views.evento_detalle, name='evento_detalle'),
]
