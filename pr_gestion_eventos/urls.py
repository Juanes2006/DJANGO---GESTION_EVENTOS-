"""
URL configuration for pr_gestion_eventos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.urls import include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_evento/', include(('app_admin.urls' , 'admin_evento'), namespace='admin_evento')),
    path('evaluadores/', include(('app_evaluadores.urls', 'evaluadores'), namespace='evaluadores')),
    path('eventos/', include(('app_eventos.urls', 'eventos'), namespace='eventos')),
    path('', include(('app_main.urls' , 'main') , namespace='main')),
    path('participantes/', include(('app_participantes.urls' , 'participantes'), namespace='participantes')),
    path('qr/', include(('app_qr.urls', 'qr'), namespace='qr')),
    path('registros/', include(('app_registros.urls', 'registros'), namespace='registros')),
    path('super_admin/', include(('app_super_admin.urls', 'super_admin'), namespace='superadmin'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

