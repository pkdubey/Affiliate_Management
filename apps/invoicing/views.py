# apps/invoicing/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Invoice
from .forms import InvoiceForm
from apps.drs.models import DailyRevenueSheet
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
import weasyprint
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.db import transaction
import logging
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        # Check if user is impersonating or is a publisher
        impersonate_publisher_id = self.request.session.get('impersonate_publisher_id')
        is_publisher = hasattr(self.request.user, 'role') and self.request.user.role == 'publisher'
        
        # Get the publisher ID (from impersonation or user's publisher)
        publisher_id = None
        if impersonate_publisher_id:
            publisher_id = impersonate_publisher_id
        elif is_publisher and hasattr(self.request.user, 'publisher'):
            publisher_id = self.request.user.publisher.id
        
        # If publisher context, force publisher tab and filter by publisher
        if publisher_id:
            queryset = Invoice.objects.filter(
                party_type='publisher',
                publisher_id=publisher_id
            ).select_related('publisher', 'advertiser')
            
            # Apply additional filters
            status = self.request.GET.get('status')
            month = self.request.GET.get('month')
            
            if status:
                queryset = queryset.filter(status=status)
            if month:
                queryset = queryset.filter(date__month=month)
                
            return queryset.order_by('-created_at')
        
        # Admin/Subadmin view - normal filtering
        party_type = self.request.GET.get('tab', 'advertiser')
        status = self.request.GET.get('status')
        client = self.request.GET.get('client')
        month = self.request.GET.get('month')
        
        queryset = Invoice.objects.select_related('publisher', 'advertiser')
        
        if party_type == 'advertiser':
            queryset = queryset.filter(party_type='advertiser')
            if client:
                queryset = queryset.filter(advertiser__id=client)
        elif party_type == 'publisher':
            queryset = queryset.filter(party_type='publisher')
            if client:
                queryset = queryset.filter(publisher__id=client)
        
        if status:
            queryset = queryset.filter(status=status)
        if month:
            queryset = queryset.filter(date__month=month)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        from apps.advertisers.models import Advertiser
        from apps.publishers.models import Publisher
        import calendar
        
        context = super().get_context_data(**kwargs)
        
        # Check if user is impersonating or is a publisher
        impersonate_publisher_id = self.request.session.get('impersonate_publisher_id')
        is_publisher = hasattr(self.request.user, 'role') and self.request.user.role == 'publisher'
        
        # Determine if we should show only publisher view
        publisher_only_view = False
        current_publisher = None
        
        if impersonate_publisher_id:
            publisher_only_view = True
            current_publisher = Publisher.objects.filter(id=impersonate_publisher_id).first()
        elif is_publisher and hasattr(self.request.user, 'publisher'):
            publisher_only_view = True
            current_publisher = self.request.user.publisher
        
        # Set context flags
        context['publisher_only_view'] = publisher_only_view
        context['current_publisher'] = current_publisher
        context['is_impersonating'] = bool(impersonate_publisher_id)
        
        if publisher_only_view:
            # Force publisher tab for publisher users
            context['active_tab'] = 'publisher'
            context['show_tabs'] = False  # Hide tab switching
            context['clients'] = Publisher.objects.filter(id=current_publisher.id) if current_publisher else []
            context['selected_client'] = str(current_publisher.id) if current_publisher else ''
        else:
            # Normal admin view with both tabs
            active_tab = self.request.GET.get('tab', 'advertiser')
            context['active_tab'] = active_tab
            context['show_tabs'] = True
            context['selected_client'] = self.request.GET.get('client', '')
            
            if active_tab == 'advertiser':
                context['clients'] = Advertiser.objects.all()
            else:
                context['clients'] = Publisher.objects.all()
        
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_month'] = self.request.GET.get('month', '')
        context['months'] = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        
        return context


class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['due_date'] = date.today() + timedelta(days=30)
        
        # Check if publisher context
        impersonate_publisher_id = self.request.session.get('impersonate_publisher_id')
        is_publisher = hasattr(self.request.user, 'role') and self.request.user.role == 'publisher'
        
        # If publisher view, set publisher as default
        if impersonate_publisher_id:
            from apps.publishers.models import Publisher
            publisher = Publisher.objects.filter(id=impersonate_publisher_id).first()
            if publisher:
                initial['publisher'] = publisher.id
                initial['party_type'] = 'publisher'
        elif is_publisher and hasattr(self.request.user, 'publisher'):
            initial['publisher'] = self.request.user.publisher.id
            initial['party_type'] = 'publisher'
        
        if drs_id := self.request.GET.get('drs'):
            try:
                drs = DailyRevenueSheet.objects.get(id=drs_id)
                initial.update({
                    'drs': drs.id,
                    'currency': 'INR',
                    'amount': drs.publisher_payout if hasattr(drs, 'publisher_payout') else 0,
                })
            except DailyRevenueSheet.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bill_from_details'] = (
            "traccify.ai\n"
            "0, Seohara Thakurdwara Road\n"
            "Seohara Uttar Pradesh 246746 India\n"
            "GSTIN: 09AMFPV3992D1ZL\n"
            "UDYAM-UP-17-0028662\n"
            "finance@traccify.ai"
        )
        
        # Pass publisher context to form
        impersonate_publisher_id = self.request.session.get('impersonate_publisher_id')
        is_publisher = hasattr(self.request.user, 'role') and self.request.user.role == 'publisher'
        
        context['publisher_only_view'] = bool(impersonate_publisher_id or is_publisher)
        context['is_impersonating'] = bool(impersonate_publisher_id)
        
        return context

    def form_valid(self, form):
        try:
            party_type = self.request.POST.get('party_type', 'advertiser')
            form.instance.party_type = party_type

            # Handle PDF only for publishers
            if party_type == 'publisher':
                if pdf := self.request.FILES.get('pdf'):
                    form.instance.pdf = pdf
            else:
                form.instance.pdf = None

            # Auto-generate invoice number
            if not form.instance.invoice_number:
                count = Invoice.objects.filter(party_type=party_type).count() + 1
                prefix = 'PUB' if party_type == 'publisher' else 'INV'
                form.instance.invoice_number = f'{prefix}-{count:06d}'

            # Attach DRS for publishers
            if party_type == 'publisher':
                drs_id = self.request.POST.get('drs')
                if drs_id:
                    try:
                        form.instance.drs = DailyRevenueSheet.objects.get(id=int(drs_id))
                    except (DailyRevenueSheet.DoesNotExist, ValueError):
                        form.instance.drs = None

            # ============================================
            # UPDATED GST LOGIC WITH CHECKBOX SUPPORT
            # ============================================
            if party_type == 'advertiser':
                amt = form.cleaned_data.get('amount') or Decimal('0')
                currency = form.cleaned_data.get('currency')
                
                # Check if GST checkbox is checked (only for INR)
                apply_gst = self.request.POST.get('apply_gst') == '1'
                
                logger.info(f"Invoice GST Calculation - Amount: {amt}, Currency: {currency}, Apply GST: {apply_gst}")
                
                if currency == 'INR' and apply_gst:
                    # Calculate 18% GST (9% CGST + 9% SGST)
                    gst = (amt * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    cgst = (amt * Decimal('0.09')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    sgst = (amt * Decimal('0.09')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    form.instance.gst_amount = gst
                    
                    # Store CGST and SGST separately if model has these fields
                    if hasattr(form.instance, 'cgst_amount'):
                        form.instance.cgst_amount = cgst
                    if hasattr(form.instance, 'sgst_amount'):
                        form.instance.sgst_amount = sgst
                    if hasattr(form.instance, 'apply_gst'):
                        form.instance.apply_gst = True
                    
                    logger.info(f"GST Applied - CGST: {cgst}, SGST: {sgst}, Total GST: {gst}")
                else:
                    # No GST for non-INR or when checkbox is unchecked
                    gst = Decimal('0.00')
                    form.instance.gst_amount = gst
                    
                    if hasattr(form.instance, 'cgst_amount'):
                        form.instance.cgst_amount = Decimal('0.00')
                    if hasattr(form.instance, 'sgst_amount'):
                        form.instance.sgst_amount = Decimal('0.00')
                    if hasattr(form.instance, 'apply_gst'):
                        form.instance.apply_gst = False
                    
                    logger.info(f"No GST Applied - Currency: {currency}, Checkbox: {apply_gst}")
                
                # Calculate total amount
                form.instance.total_amount = (amt + gst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                logger.info(f"Final Total: {form.instance.total_amount}")

            # Save the instance
            self.object = form.save()

            # AJAX JSON response
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': self.get_success_url(),
                    'message': f'Invoice {form.instance.invoice_number} created successfully!',
                    'invoice_data': {
                        'invoice_number': form.instance.invoice_number,
                        'amount': str(form.instance.amount),
                        'gst_amount': str(form.instance.gst_amount),
                        'total_amount': str(form.instance.total_amount),
                        'currency': form.instance.currency
                    }
                })

            messages.success(self.request, f'Invoice {form.instance.invoice_number} created successfully!')
            return redirect(self.get_success_url())

        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}", exc_info=True)
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating invoice: {str(e)}',
                    'errors': {'__all__': [str(e)]}
                }, status=500)
            
            messages.error(self.request, f'Error creating invoice: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error(f"Form validation errors: {form.errors}")
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors below.'
            }, status=400)
        
        return super().form_invalid(form)

    def get_success_url(self):
        party_type = self.request.POST.get('party_type', 'advertiser')
        tab = 'publisher' if party_type == 'publisher' else 'advertiser'
        return reverse('invoicing:invoice_list') + f'?tab={tab}'

class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'
    success_url = reverse_lazy('invoicing:invoice_list')

    def form_valid(self, form):
        old_status = self.object.status
        new_status = form.cleaned_data.get('status', 'Pending')
        
        # If status changed to Paid, update related DRS
        if old_status != 'Paid' and new_status == 'Paid':
            if self.object.drs:
                self.object.drs.status = 'paid'
                self.object.drs.save()
        
        messages.success(self.request, f'Invoice {form.instance.invoice_number} updated successfully!')
        return super().form_valid(form)


class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'invoicing/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoicing:invoice_list')


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoicing/invoice_detail.html'
    context_object_name = 'invoice'


class InvoiceExportView(TemplateView):
    template_name = 'invoicing/invoice_export.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') != 'csv':
            return super().get(request, *args, **kwargs)
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoices.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Invoice Number', 'Party Type', 'Status', 'Amount', 'Total', 'Created'])
        for invoice in Invoice.objects.all():
            writer.writerow([
                invoice.id,
                invoice.invoice_number,
                invoice.get_party_type_display(),
                invoice.get_status_display(),
                invoice.amount,
                invoice.total_amount,
                invoice.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        return response


class InvoicePDFView(View):
    """Generate PDF version of invoice using the improved dynamic template"""
    
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        
        try:
            context = {
                'invoice': invoice,
                'cgst': getattr(invoice, 'cgst_amount', invoice.gst_amount / 2 if invoice.currency == 'INR' else 0),
                'sgst': getattr(invoice, 'sgst_amount', invoice.gst_amount / 2 if invoice.currency == 'INR' else 0),
                'invoice_lines': getattr(invoice, 'lines', None),
            }
            
            if not context['invoice_lines'] or not context['invoice_lines'].exists():
                context['default_service'] = {
                    'description': 'Service',
                    'quantity': 48,
                    'rate': 50,
                    'amount': 2400
                }
            
            html = render_to_string('invoice_pdf_template.html', context)
            pdf = weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
            
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="invoice_{invoice.invoice_number}.pdf"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating PDF for invoice {pk}: {str(e)}")
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect('invoicing:detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class MyInvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/affiliate_invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        if hasattr(self.request.user, 'publisher'):
            return Invoice.objects.filter(publisher=self.request.user.publisher)
        return Invoice.objects.none()
