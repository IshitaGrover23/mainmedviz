from django import forms
from .models import ChestXRay

class ChestXRayForm(forms.ModelForm):
    class Meta:
        model = ChestXRay
        fields = ['image']