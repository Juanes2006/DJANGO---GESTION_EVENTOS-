from django.urls import path
from . import views

app_name = 'registros'

urlpatterns = [
    path('<int:evento_id>/registrarme/', views.registrarme_evento, name='registrarme_evento'),
    path('cancelar_inscripcion/<int:evento_id>/<str:user_id>/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
]
