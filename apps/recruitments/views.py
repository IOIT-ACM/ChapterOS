from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib import messages

def is_team_or_admin(user):
    if user.is_authenticated:
        return user.groups.filter(name__in=['Team', 'Admin']).exists()
    return False

@login_required
def index(request):
    """
    Displays the main recruitments page with cards for different drives.
    """
    return render(request, "recruitments/index.html")

@login_required
def recruitment_responses_view(request):
    """
    Renders the HTML shell for the recruitment responses page.
    All data fetching and rendering is handled by client-side JavaScript.
    """
    user_groups = set(request.user.groups.values_list('name', flat=True))
    can_view_sensitive_data = any(role in user_groups for role in ['Admin', 'Core', 'Advisory'])

    context = {
        'recruitment_drive_name': "ACM Committee Recruitment 2025-26 (July 2025)",
        'can_view_sensitive_data': can_view_sensitive_data,
    }
    return render(request, "recruitments/responses.html", context)