from django import forms
from .models import Form

class FormCreateForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['title', 'description', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].required = False