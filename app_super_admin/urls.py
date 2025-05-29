
from django.urls import path
from . import views

urlpatterns = [
    path('', views.super_admin, name='super_admin'),
    path('eventos/', views.eventos_superadmin, name='eventos_superadmin'),
    path('evento/<int:eve_id>/', views.ver_evento_superadmin, name='ver_evento_superadmin'),
    path('agregar_area/', views.agregar_area, name='agregar_area'),
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
]
