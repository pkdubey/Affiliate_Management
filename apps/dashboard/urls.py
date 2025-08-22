from django.urls import path
from . import views
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

app_name = 'dashboard'

@login_required
def root_redirect(request):
    if request.user.role == 'publisher':
        return redirect('dashboard:publisher_dashboard')
    elif request.user.role in ['admin', 'subadmin', 'dashboard']:
        return redirect('dashboard:admin_dashboard')
    return redirect('dashboard:default_dashboard')

urlpatterns = [
    path('', root_redirect, name='root_redirect'),
    path('admin/', views.dashboard_view, name='admin_dashboard'),
    path('publisher/', views.publisher_dashboard, name='publisher_dashboard'),
    path('default/', views.default_dashboard, name='default_dashboard'),
]