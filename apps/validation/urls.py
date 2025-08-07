
from django.urls import path
from .views import (
    ValidationListView, ValidationCreateView, ValidationUpdateView, ValidationDeleteView, ValidationDetailView
)
import apps.validation.views as views

app_name = 'validation'

urlpatterns = [
    path('', ValidationListView.as_view(), name='validation_list'),
    path('add/', ValidationCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', ValidationUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ValidationDeleteView.as_view(), name='delete'),
    path('<int:pk>/', ValidationDetailView.as_view(), name='detail'),
    path('export/', views.ValidationExportView.as_view(), name='validation_export'),
]
