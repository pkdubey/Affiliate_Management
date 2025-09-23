from django.urls import path
from .views import (
    PublisherListView, PublisherCreateView, PublisherUpdateView, PublisherDeleteView, PublisherDetailView, PublisherWishlistUploadView, PublisherPortalView,
    start_impersonate, impersonated_dashboard, stop_impersonate
)
from . import views

app_name = 'publishers'

urlpatterns = [
    path('', PublisherListView.as_view(), name='publisher_list'),
    path('add/', PublisherCreateView.as_view(), name='add'),
    path('<int:publisher_id>/wishlist/', views.publisher_wishlist_ajax, name='publisher_wishlist'),
    path('<int:pk>/edit/', PublisherUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', PublisherDeleteView.as_view(), name='delete'),
    path('<int:pk>/', PublisherDetailView.as_view(), name='detail'),
    path('upload/', views.PublisherWishlistUploadView.as_view(), name='wishlist_upload'),
    path('portal/', views.PublisherPortalView.as_view(), name='portal'),
    path('<int:publisher_id>/impersonate/', start_impersonate, name='impersonate'),
    path('<int:publisher_id>/as/', impersonated_dashboard, name='impersonated_dashboard'),
    path('stop-impersonate/', stop_impersonate, name='stop_impersonate'),
]
