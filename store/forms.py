from django import forms
from .models import reviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = reviewRating
        fields = ['subject', 'reviews', 'rating',]