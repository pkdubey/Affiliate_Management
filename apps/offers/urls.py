
from django.urls import path
from .views import (
    OfferListView, OfferCreateView, OfferUpdateView, OfferDeleteView, OfferDetailView, OffersMatcherView
)
from .views import OffersMatcherResultsView

app_name = 'offers'

urlpatterns = [
    path('matcher/', OffersMatcherView.as_view(), name='offers_matcher'),
    path('results/', OffersMatcherResultsView.as_view(), name='matcher_results'),
    path('add/', OfferCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', OfferUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', OfferDeleteView.as_view(), name='delete'),
    path('<int:pk>/', OfferDetailView.as_view(), name='detail'),
]
