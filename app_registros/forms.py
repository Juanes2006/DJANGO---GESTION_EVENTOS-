from django import forms

TIPOS_INSCRIPCION = (
    ('Asistente', 'Asistente'),
    ('Participante', 'Participante'),
    ('Evaluador', 'Evaluador'),
)

class RegistroEventoForm(forms.Form):
    tipo_inscripcion = forms.ChoiceField(choices=TIPOS_INSCRIPCION, required=True)
    user_id = forms.IntegerField(required=True)
    username = forms.CharField(max_length=150, required=True)
    nombre = forms.CharField(max_length=150, required=True)
    correo = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=20, required=True)

    # Campos de archivos, opcionales según tipo_inscripcion
    soporte_pago = forms.FileField(required=False)
    documentos_participante = forms.FileField(required=False)
    documentos_evaluador = forms.FileField(required=False)
