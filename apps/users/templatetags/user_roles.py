from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    if not user or not user.is_authenticated:
        return False
    # Check both lowercase and original case
    return str(user.role).lower() == str(role_name).lower()