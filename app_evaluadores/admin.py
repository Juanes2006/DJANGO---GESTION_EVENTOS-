from django.contrib import admin
from .models import Evaluador, Criterio, Calificacion, Instrumento

@admin.register(Evaluador)
class EvaluadorAdmin(admin.ModelAdmin):
    list_display = ('eva_id', 'eva_nombre', 'eva_correo', 'eva_telefono')
    search_fields = ('eva_nombre', 'eva_correo')

@admin.register(Criterio)
class CriterioAdmin(admin.ModelAdmin):
    list_display = ('cri_id', 'cri_descripcion', 'cri_peso', 'cri_evento_fk')
    search_fields = ('cri_descripcion',)

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cal_evaluador_fk', 'cal_criterio_fk', 'cal_participante_fk', 'cal_valor')
    list_filter = ('cal_evaluador_fk', 'cal_criterio_fk')

@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('inst_id', 'inst_tipo', 'inst_descripcion', 'inst_evento_fk')
    search_fields = ('inst_tipo',)

