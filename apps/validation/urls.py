from django.urls import path
from .views import (
    ValidationListView, ValidationCreateView, ValidationUpdateView,
    ValidationDeleteView, ValidationDetailView, ValidationExportView,
    ValidationTabView, SaveReportView, MyValidationView, UploadInvoiceView,
    InvoiceApprovalView, GenerateInvoiceView, BulkApproveValidationsView, CheckUserStatusView
)

app_name = 'validation'

urlpatterns = [
    # Existing URLs
    path('', ValidationListView.as_view(), name='validation_list'),
    path('add/', ValidationCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', ValidationUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ValidationDeleteView.as_view(), name='delete'),
    path('<int:pk>/', ValidationDetailView.as_view(), name='detail'),
    path('export/', ValidationExportView.as_view(), name='validation_export'),
    
    # New Validation Tab URLs (Validation Workflow)
    path('tab/', ValidationTabView.as_view(), name='validation_tab'),
    path('save-report/', SaveReportView.as_view(), name='save_report'),
    path('my-validation/', MyValidationView.as_view(), name='my_validation'),
    
    # Invoice URLs
    path('upload-invoice/<int:validation_id>/', UploadInvoiceView.as_view(), name='upload_invoice'),
    path('generate-invoice/<int:validation_id>/', GenerateInvoiceView.as_view(), name='generate_invoice'),
    path('invoice/<int:invoice_id>/approve/', InvoiceApprovalView.as_view(), name='approve_invoice'),
    
    # Bulk Actions
    path('bulk-approve/', BulkApproveValidationsView.as_view(), name='bulk_approve'),
    
    # Status Update URLs
    path('<int:pk>/approve/', ValidationUpdateView.as_view(), name='approve_validation'),
    path('<int:pk>/reject/', ValidationUpdateView.as_view(), name='reject_validation'),
    path('<int:pk>/mark-invoiced/', ValidationUpdateView.as_view(), name='mark_invoiced'),
    path('<int:pk>/mark-paid/', ValidationUpdateView.as_view(), name='mark_paid'),
    path('save-report/', SaveReportView.as_view(), name='save_report'),
    path('check-user-status/', CheckUserStatusView.as_view(), name='check_user_status'),
]