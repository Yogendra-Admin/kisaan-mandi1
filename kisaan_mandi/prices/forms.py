from django import forms
from .models import MarketPrice

class MarketPriceForm(forms.ModelForm):
    class Meta:
        model = MarketPrice
        fields = ['crop_name', 'mandi_name', 'state', 'min_price', 'max_price', 'modal_price', 'unit', 'date', 'trend']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

for field in MarketPriceForm.base_fields.values():
    if hasattr(field.widget, 'attrs'):
        cn = field.widget.__class__.__name__
        if cn in ['TextInput','NumberInput','DateInput']:
            field.widget.attrs['class'] = 'form-control'
        elif cn == 'Select':
            field.widget.attrs['class'] = 'form-select'
