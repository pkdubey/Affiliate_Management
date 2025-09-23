from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """Return True if user.role equals role_name (case-insensitive)."""
    if not user or not user.is_authenticated:
        return False
    return str(user.role).lower() == str(role_name).lower()


@register.filter
def dict_get(mapping, key):
    """
    Template helper:  {{ my_dict|dict_get:some_key }}
    Safely fetch mapping[key] or None.
    """
    if isinstance(mapping, dict):
        return mapping.get(key)
    return None