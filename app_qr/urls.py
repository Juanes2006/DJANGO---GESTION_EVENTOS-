from django.urls import path
from . import views

app_name = 'qr'

urlpatterns = [
    path('consulta_qr/', views.consulta_qr, name='consulta_qr'),
    path('mostrar_qr/<int:event_id>/<str:user_id>/', views.mostrar_qr, name='mostrar_qr'),
    path('descargar_qr/<int:event_id>/<str:user_id>/', views.descargar_qr, name='descargar_qr'),
]
