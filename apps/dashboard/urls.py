from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.dashboard_view, name='admin_dashboard'),
    path('', views.dashboard_view, name='dashboard'),  # admin dashboard
    path('publisher/', views.publisher_dashboard, name='publisher_dashboard'),  # publisher dashboard
]
