from django import forms
from store.models import ReviewRating

class ReviewForm(forms.ModelForm):

    class Meta:
        model = ReviewRating
        fields = ["subject","review","rating"]

        widgets = {
            'subject':forms.TextInput(attrs={
                'placeholder':'Review Title',
                'class':'form-control'
            }),
            'review':forms.Textarea(attrs={
                'placeholder':'Enter your thoughts',
                'class':'form-control'
            }),
        }