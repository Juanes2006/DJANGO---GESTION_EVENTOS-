# app_eventos/urls.py
from django.urls import path
from . import views

app_name = "eventos"

urlpatterns = [
    path('crear/', views.crear_evento, name="eventos_crear_evento"),
    path('editar/<int:pk>/', views.editar_evento, name="editar_evento"),
    path('cancelar/<int:pk>/', views.cancelar_evento, name="cancelar_evento"),
    path('activar/<int:pk>/', views.activar_evento, name="activar_evento"),
    path('evento/<int:eve_id>/eliminar/', views.eliminar_evento, name='eliminar_evento'),

    path('desactivar/<int:pk>/', views.desactivar_evento, name="desactivar_evento"),
    path('descargar/<int:pk>/', views.descargar_programacion, name="descargar_programacion"),
]
