from django import forms

class RegistroEventoForm(forms.Form):
    TIPO_INSCRIPCION_CHOICES = [
        ('Asistente', 'Asistente'),
        ('Participante', 'Participante'),
        ('Evaluador','Evaluador')
    ]

    tipo_inscripcion = forms.ChoiceField(choices=TIPO_INSCRIPCION_CHOICES)
    user_id = forms.CharField(label='Documento de identidad')
    nombre = forms.CharField(label='Nombre completo')
    correo = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(label='Teléfono')
    soporte_pago = forms.FileField(required=False)
    documentos = forms.FileField(required=False)
