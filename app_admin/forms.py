from django import forms
from .models import PlantillaCertificado

class PlantillaCertificadoForm(forms.ModelForm):
    class Meta:
        model = PlantillaCertificado
        fields = "__all__"

        widgets = {
            # Colores
            "color_fondo": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
            "color_borde": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
            "color_titulo": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
            "color_nombre": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),

            # Posiciones con slider
            "pos_titulo_y": forms.NumberInput(attrs={"type": "range", "min": "100", "max": "800", "step": "10", "class": "form-range"}),
            "pos_subtitulo_y": forms.NumberInput(attrs={"type": "range", "min": "100", "max": "800", "step": "10", "class": "form-range"}),
            "pos_nombre_y": forms.NumberInput(attrs={"type": "range", "min": "100", "max": "800", "step": "10", "class": "form-range"}),

            # Otros campos para que se vean consistentes
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "subtitulo": forms.TextInput(attrs={"class": "form-control"}),
            "texto_firma": forms.TextInput(attrs={"class": "form-control"}),

            "tamano_titulo": forms.NumberInput(attrs={"class": "form-control", "min": "8", "max": "72"}),
            "tamano_nombre": forms.NumberInput(attrs={"class": "form-control", "min": "8", "max": "72"}),

            "fuente_titulo": forms.Select(attrs={"class": "form-select"}),
            "fuente_nombre": forms.Select(attrs={"class": "form-select"}),

            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "sello": forms.FileInput(attrs={"class": "form-control"}),

            "borde_grosor": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "10"}),
            "borde_margen": forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "200"}),

            "mostrar_firma": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
