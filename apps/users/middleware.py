from django.core.exceptions import PermissionDenied
from django.urls import reverse

class VisitorAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            is_visitor_only = request.user.groups.filter(name='Visitor').exists() and request.user.groups.count() == 1
            
            if is_visitor_only:
                logout_url = reverse('users:logout')
                
                if not request.user.is_staff and request.path != logout_url:
                    raise PermissionDenied("Your account is pending approval. You do not have permission to access this site.")

        return self.get_response(request)