from django import forms
from .models import Form

class FormCreateForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['title', 'description', 'deadline', 'confirmation_message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
            'confirmation_message': forms.Textarea(attrs={'rows': 2, 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].required = False
        self.fields['description'].required = False
        self.fields['confirmation_message'].required = False

class FormSettingsForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['title', 'description', 'slug', 'is_active', 'deadline', 'confirmation_message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'slug': forms.TextInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
            'confirmation_message': forms.Textarea(attrs={'rows': 2, 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-orange-600 bg-neutral-700 border-neutral-600 rounded focus:ring-orange-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].required = False
        self.fields['description'].required = False
        self.fields['confirmation_message'].required = False