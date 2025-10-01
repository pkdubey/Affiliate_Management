
from django.urls import path
from .views import (
    AdvertiserListView, AdvertiserCreateView, AdvertiserUpdateView, AdvertiserDeleteView, AdvertiserDetailView, AdvertiserOfferUploadView
)
import apps.advertisers.views as views

app_name = 'advertisers'

urlpatterns = [
    path('', views.AdvertiserListView.as_view(), name='advertiser_list'),  
    path('add/', views.AdvertiserCreateView.as_view(), name='add'),
    path('<int:advertiser_id>/offers/', views.advertiser_offers_ajax, name='advertiser_offers_ajax'),
    path('<int:pk>/edit/', views.AdvertiserUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AdvertiserDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.AdvertiserDetailView.as_view(), name='detail'),
    path('upload/', views.AdvertiserOfferUploadView.as_view(), name='offer_upload'),
]


