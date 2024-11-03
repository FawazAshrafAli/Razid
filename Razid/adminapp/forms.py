from django import forms
from .models import Product

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_image',)