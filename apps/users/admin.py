from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'full_name', 'team', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {'fields': ('full_name', 'mobile_number', 'academic_year', 'branch', 'team')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Information', {'fields': ('full_name', 'mobile_number', 'academic_year', 'branch', 'team')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)