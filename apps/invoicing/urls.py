
from django.urls import path
from .views import (
    InvoiceListView, InvoiceCreateView, InvoiceUpdateView, InvoiceDeleteView, InvoiceDetailView, InvoiceExportView, InvoicePDFView, UpdateInvoiceStatusView
)

app_name = 'invoicing'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('add/', InvoiceCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', InvoiceUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', InvoiceDeleteView.as_view(), name='delete'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='detail'),
    path('export/', InvoiceExportView.as_view(), name='invoice_export'),
    path('<int:pk>/pdf/', InvoicePDFView.as_view(), name='pdf'),
    path('<int:pk>/update-status/', UpdateInvoiceStatusView.as_view(), name='update_status'),
]
