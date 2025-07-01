def user_roles(request):
    """
    Adds the user's group names to the context.
    This allows us to check roles like `{% if 'Admin' in user_roles %}` in templates.
    """
    if request.user.is_authenticated:
        roles = list(request.user.groups.values_list('name', flat=True))
        return {'user_roles': roles}
    return {'user_roles': []}