
from django.urls import path
from .views import (
    DailyRevenueSheetListView, DailyRevenueSheetCreateView, DailyRevenueSheetUpdateView, DailyRevenueSheetDeleteView, DailyRevenueSheetDetailView, DRSExportView, drs_currency_amount_api, DRSForValidationView
)

app_name = 'drs'

urlpatterns = [
    path('', DailyRevenueSheetListView.as_view(), name='drs_list'),
    path('add/', DailyRevenueSheetCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', DailyRevenueSheetUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', DailyRevenueSheetDeleteView.as_view(), name='delete'),
    path('<int:pk>/', DailyRevenueSheetDetailView.as_view(), name='detail'),
    path('export/', DRSExportView.as_view(), name='drs_export'),
    path('api/get_amount/', drs_currency_amount_api, name='drs_get_amount'),
    path('for-validation/', DRSForValidationView.as_view(), name='for_validation'),
]
