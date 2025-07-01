from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages

def is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

def is_admin(user):
    return user.is_authenticated and is_in_group(user, 'Admin')

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            visitor_group, created = Group.objects.get_or_create(name='Visitor')
            user.groups.add(visitor_group)
            
            messages.success(request, 'Registration successful! Please sign in.')
            return redirect('users:login')
        
        return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html')


@user_passes_test(is_admin, login_url='users:dashboard')
def admin_conference_view(request):
    return render(request, 'users/admin_conference.html')