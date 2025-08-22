from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            print(f"ROLE DECORATOR: User {user.username}, Role: {user.role}")
            print(f"ROLE DECORATOR: Allowed roles: {allowed_roles}")
            
            # Check if user has the required role
            if user.role in allowed_roles:
                print(f"ROLE DECORATOR: Access granted")
                return view_func(request, *args, **kwargs)
            else:
                print(f"ROLE DECORATOR: Access denied. Redirecting to default dashboard")
                return redirect('dashboard:default_dashboard')
            
        return wrapper
    return decorator