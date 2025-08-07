from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """
    Checks if the user has a given role. Supports 'is_admin', 'is_subadmin', and 'is_superuser'.
    """
    if not user.is_authenticated:
        return False
    if role_name == 'admin':
        return getattr(user, 'is_admin', False)
    if role_name == 'subadmin':
        return getattr(user, 'is_subadmin', False)
    if role_name == 'superuser':
        return user.is_superuser
    return False
