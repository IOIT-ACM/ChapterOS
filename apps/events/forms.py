from django import forms
from .models import Event, EventCategory

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'start_time', 'end_time', 'location', 'is_all_day', 
            'category', 'status', 'registration_required', 'max_participants',
            'is_recurring', 'privacy'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'description': forms.Textarea(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'rows': 3, 'placeholder': ' '}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer'}),
            'location': forms.TextInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
            'category': forms.Select(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500'}),
            'status': forms.Select(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500'}),
            'privacy': forms.Select(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500'}),
            'max_participants': forms.NumberInput(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer', 'placeholder': ' '}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = EventCategory.objects.all()
        self.fields['category'].empty_label = "Select a category..."
        self.fields['end_date'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        self.fields['max_participants'].required = False