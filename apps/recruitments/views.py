import requests
import csv
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

@login_required
@user_passes_test(is_team_or_admin)
def export_responses_csv(request):
    """
    Exports all recruitment responses to a CSV file.
    This remains a server-side function.
    """
    api_url = "https://ioit.acm.org/api/recruitment/all"
    try:
        headers = {'Origin': 'https://os.ioit.acm.org'}
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        responses_data = response.json()
    except requests.exceptions.RequestException:
        messages.error(request, "Could not fetch data from the API to generate the CSV.")
        return redirect('recruitments:recruitment_responses')

    if not responses_data:
        messages.error(request, "No data available to export.")
        return redirect('recruitments:recruitment_responses')

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="acm_committee_recruitment_2025-26.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    
    if responses_data:
        headers = responses_data[0].keys()
        writer.writerow(headers)
        for item in responses_data:
            row_values = [str(item.get(h, '')).encode('utf-8', 'replace').decode('utf-8') for h in headers]
            writer.writerow(row_values)

    return response