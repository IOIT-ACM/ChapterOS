from django import forms
from .models import Event, EventCategory, AcademicYear

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'start_time', 'end_time', 'location', 'category', 
            'status', 'privacy', 'academic_years'
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
            'academic_years': forms.SelectMultiple(attrs={'class': 'block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = EventCategory.objects.all()
        self.fields['category'].empty_label = "Select a category..."
        self.fields['end_date'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        self.fields['academic_years'].queryset = AcademicYear.objects.all()
        self.fields['academic_years'].required = True

class BulkUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file',
        widget=forms.FileInput(attrs={'class': 'block w-full text-sm text-neutral-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-600 file:text-white hover:file:bg-orange-700 cursor-pointer', 'accept': '.csv'})
    )

    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError("File is not a CSV type")
        return file