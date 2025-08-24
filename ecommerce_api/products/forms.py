from django import forms
from django.contrib.auth import get_user_model
from .models import Product, ProductReview, ProductImage
from django.core.exceptions import ValidationError

CustomUser = get_user_model()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'price', 'compare_price', 'cost',
            'sku', 'barcode', 'quantity', 'low_stock_threshold', 'category',
            'brand', 'status', 'is_featured', 'is_digital', 'weight', 'length',
            'width', 'height', 'seo_title', 'seo_description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'seo_description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'order']

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})