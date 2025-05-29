from django import forms
from .models import Evaluador

class EvaluadorForm(forms.ModelForm):
    class Meta:
        model = Evaluador
        fields = '__all__'
