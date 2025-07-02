from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.core.cache import cache
import requests
from django.http import JsonResponse

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
    Data is fetched asynchronously by the client.
    """
    user_groups = set(request.user.groups.values_list('name', flat=True))
    can_view_sensitive_data = any(role in user_groups for role in ['Admin', 'Core', 'Advisory'])

    questions_cache_key = 'form_data_acm_25_json'
    questions_map = cache.get(questions_cache_key)

    if not questions_map:
        try:
            url = "https://ioit.acm.org/api/formdata/acm.25.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            questions_map = response.json()
            cache.set(questions_cache_key, questions_map)
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            questions_map = {}

    context = {
        'recruitment_drive_name': "ACM Committee Recruitment 2025-26 (July 2025)",
        'can_view_sensitive_data': can_view_sensitive_data,
        'questions_map': questions_map,
    }
    return render(request, "recruitments/responses.html", context)

@login_required
def recruitment_data_api(request):
    """
    API endpoint to fetch, process, and return recruitment data.
    """
    user_groups = set(request.user.groups.values_list('name', flat=True))
    can_view_sensitive_data = any(role in user_groups for role in ['Admin', 'Core', 'Advisory'])

    responses_cache_key = 'recruitment_responses_acm_25'
    applicants_data = cache.get(responses_cache_key)

    if not applicants_data:
        try:
            url = "https://ioit.acm.org/api/recruitment/all"
            headers = {'Origin': 'https://os.ioit.acm.org'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            applicants_data = response.json()
            cache.set(responses_cache_key, applicants_data, timeout=60 * 5)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            return JsonResponse({'error': f"Failed to fetch data from external API: {e}"}, status=502)

    if not can_view_sensitive_data:
        sanitized_data = []
        for applicant in applicants_data:
            sanitized_data.append({
                **applicant,
                'fullName': f"Applicant #{applicant.get('id', 'N/A')}",
                'mobile': "[Hidden]",
                'branch': "",
                'year': "",
            })
        applicants_data = sanitized_data

    return JsonResponse(applicants_data, safe=False)