from django import forms
from .models import Encomienda


class EncomiendaForm(forms.ModelForm):
    class Meta:
        model = Encomienda
        fields = [
            'descripcion', 'peso_kg', 'volumen_cm3',
            'remitente', 'destinatario', 'ruta',
            'fecha_entrega_est', 'observaciones',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }
