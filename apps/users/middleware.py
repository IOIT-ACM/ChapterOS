from django.core.exceptions import PermissionDenied
from django.urls import reverse

class VisitorAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            is_visitor_only = request.user.groups.filter(name='Visitor').exists() and request.user.groups.count() == 1
            
            if is_visitor_only:
                allowed_paths = [
                    reverse('landing_page'),
                    reverse('users:dashboard'),
                    reverse('users:profile'),
                    reverse('users:logout'),
                ]
                
                if request.path not in allowed_paths:
                    raise PermissionDenied("As a Visitor, you do not have permission to access this page. Your account is pending approval.")

        return self.get_response(request)