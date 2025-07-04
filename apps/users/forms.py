from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'mobile_number', 'academic_year', 'branch', 'team')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'mobile_number', 'academic_year', 'branch', 'team']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        text_input_classes = "block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500 peer"
        
        select_input_classes = "block py-2.5 px-0 w-full text-sm text-white bg-transparent border-0 border-b-2 border-neutral-600 appearance-none focus:outline-none focus:ring-0 focus:border-orange-500"

        self.fields['full_name'].widget.attrs.update({'class': text_input_classes, 'placeholder': ' '})
        self.fields['email'].widget.attrs.update({'class': text_input_classes, 'placeholder': ' '})
        self.fields['mobile_number'].widget.attrs.update({'class': text_input_classes, 'placeholder': ' '})
        
        self.fields['academic_year'].widget.attrs.update({'class': select_input_classes})
        self.fields['branch'].widget.attrs.update({'class': select_input_classes})
        self.fields['team'].widget.attrs.update({'class': select_input_classes})