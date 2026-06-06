from django import forms
from .models import Product, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price_per_unit', 'unit', 'quantity_available', 'image', 'location', 'state', 'is_organic']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

for field in ProductForm.base_fields.values():
    if hasattr(field.widget, 'attrs'):
        cn = field.widget.__class__.__name__
        if cn in ['TextInput','NumberInput']:
            field.widget.attrs['class'] = 'form-control'
        elif cn == 'Select':
            field.widget.attrs['class'] = 'form-select'
        elif cn == 'Textarea':
            field.widget.attrs['class'] = 'form-control'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
