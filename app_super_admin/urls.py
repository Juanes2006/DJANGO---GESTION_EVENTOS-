
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.super_admin, login_url='main:login'), name='super_admin'),
    path('eventos/', login_required(views.eventos_superadmin, login_url='main:login'), name='eventos_superadmin'),
    path('evento/<int:eve_id>/', login_required(views.ver_evento_superadmin, login_url='main:login'), name='ver_evento_superadmin'),
    path('agregar_area/', login_required(views.agregar_area, login_url='main:login'), name='agregar_area'),
    path('agregar_categoria/', login_required(views.agregar_categoria, login_url='main:login'), name='agregar_categoria'),
    
    
# urls.py
    path('panel-aprobaciones/', login_required(views.panel_aprobaciones_view, login_url='main:login'), name='panel_aprobaciones'),
    path('aprobar_admin/<int:admin_id>/', views.aprobar_admin, name='aprobar_admin'),
    path('cambiar_estado_admin/<int:admin_id>/', views.cambiar_estado_admin, name='cambiar_estado_admin'),

]
