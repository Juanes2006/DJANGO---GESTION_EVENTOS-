from django.urls import path
from . import views

app_name = 'asistente'

urlpatterns = [
    path('panel/', views.panel_asistente, name='panel_asistente'),
]
