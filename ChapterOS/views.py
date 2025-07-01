from django.shortcuts import render

def custom_error_view(request, exception=None, status_code=None):
    context = {
        'status_code': status_code,
        'reason_phrase': "Error",
        'message': "An unexpected error occurred.",
    }

    if status_code == 400:
        context['reason_phrase'] = "Bad Request"
        context['message'] = "The server could not understand the request due to invalid syntax."
    elif status_code == 403:
        context['reason_phrase'] = "Forbidden"
        context['message'] = getattr(exception, 'message', "You do not have permission to access this page.")
    elif status_code == 404:
        context['reason_phrase'] = "Page Not Found"
        context['message'] = "The page you are looking for might have been removed, had its name changed, or is temporarily unavailable."
    elif status_code == 500:
        context['reason_phrase'] = "Internal Server Error"
        context['message'] = "We are experiencing some technical difficulties. Please try again later."

    return render(request, 'global/error.html', context, status=status_code)

def handler400(request, exception):
    return custom_error_view(request, exception, status_code=400)

def handler403(request, exception):
    return custom_error_view(request, exception, status_code=403)

def handler404(request, exception):
    return custom_error_view(request, exception, status_code=404)

def handler500(request):
    return custom_error_view(request, status_code=500)