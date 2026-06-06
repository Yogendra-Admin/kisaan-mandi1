from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'delivery_address', 'payment_method', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class CartOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'payment_method', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

for form_class in [OrderForm, CartOrderForm]:
    for field in form_class.base_fields.values():
        if hasattr(field.widget, 'attrs'):
            cn = field.widget.__class__.__name__
            if cn in ['TextInput','NumberInput']:
                field.widget.attrs['class'] = 'form-control'
            elif cn == 'Select':
                field.widget.attrs['class'] = 'form-select'
            elif cn == 'Textarea':
                field.widget.attrs['class'] = 'form-control'
