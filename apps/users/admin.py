from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'position', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('position',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('position',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)