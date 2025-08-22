"""
URL configuration for affiliate_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect(request):
    print(f"DEBUG: User {request.user.username} with role {request.user.role} is being redirected")
    if request.user.role == 'publisher':
        print("DEBUG: Redirecting to publisher dashboard")
        return redirect('/panel/dashboard/publisher/')  # Use direct URL
    elif request.user.role in ['admin', 'subadmin', 'dashboard']:
        print("DEBUG: Redirecting to admin dashboard")
        return redirect('/panel/dashboard/admin/')  # Use direct URL
    print("DEBUG: Fallback to default dashboard")
    return redirect('/panel/dashboard/default/')  # Use direct URL

admin.site.site_header = "Traccify.ai Admin Panel"
admin.site.site_title = "Traccify.ai Admin"
admin.site.index_title = "Welcome to the Traccify.ai Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('panel/dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('panel/dashboard/', include('apps.dashboard.urls', namespace='dashboard')),  # REMOVE OR COMMENT THIS LINE
    path('panel/advertisers/', include('apps.advertisers.urls', namespace='advertisers')),
    path('panel/publishers/', include('apps.publishers.urls', namespace='publishers')),
    path('panel/offers/', include('apps.offers.urls', namespace='offers')),
    path('panel/invoicing/', include('apps.invoicing.urls', namespace='invoicing')),
    path('panel/drs/', include('apps.drs.urls', namespace='drs')),
    path('panel/validation/', include('apps.validation.urls', namespace='validation')),
    path('panel/users/', include('apps.users.urls', namespace='users')),
]