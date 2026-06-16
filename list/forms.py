from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item              # Which model this form is based on
        fields = ['title', 'description']   # Which fields to show
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-green-500 transition',
                'placeholder': 'Enter title here...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-green-500 transition h-36',
                'placeholder': 'Enter description here...'
            }),
        }