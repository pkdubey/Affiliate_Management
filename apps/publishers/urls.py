
from django.urls import path
from .views import (
    PublisherListView, PublisherCreateView, PublisherUpdateView, PublisherDeleteView, PublisherDetailView, PublisherWishlistUploadView, PublisherPortalView
)
from . import views

app_name = 'publishers'

urlpatterns = [
    path('', PublisherListView.as_view(), name='publisher_list'),
    path('add/', PublisherCreateView.as_view(), name='add'),
    path('<int:publisher_id>/wishlist/', views.publisher_wishlist_ajax, name='publisher_wishlist_ajax'),
    path('<int:pk>/edit/', PublisherUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', PublisherDeleteView.as_view(), name='delete'),
    path('<int:pk>/', PublisherDetailView.as_view(), name='detail'),
    path('upload/', views.PublisherWishlistUploadView.as_view(), name='wishlist_upload'),
    path('portal/', views.PublisherPortalView.as_view(), name='portal'),
]
