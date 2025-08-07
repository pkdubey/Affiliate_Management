from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Invoice
from .forms import InvoiceForm
from apps.drs.models import DailyRevenueSheet
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/invoice_list.html'
    context_object_name = 'invoices'

class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'
    success_url = reverse_lazy('invoicing:invoice_list')

    def get_initial(self):
        initial = super().get_initial()
        drs_id = self.request.GET.get('drs')
        if drs_id:
            try:
                from apps.drs.models import DailyRevenueSheet
                drs = DailyRevenueSheet.objects.get(id=drs_id)
                initial.update({
                    'drs': drs.id,
                    'currency': 'INR',
                    'amount': drs.publisher_payout,
                })
            except DailyRevenueSheet.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Place your company info here or fetch from your config
        context['bill_from_details'] = (
            "traccify.ai\n"
            "0, Seohara Thakurdwara Road\n"
            "Seohara Uttar Pradesh 246746 India\n"
            "GSTIN: 09AMFPV3992D1ZL\n"
            "UDYAM-UP-17-0028662\n"
            "finance@traccify.ai"
        )
        return context

class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'
    success_url = reverse_lazy('invoicing:invoice_list')

class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'invoicing/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoicing:list')

class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoicing/invoice_detail.html'
    context_object_name = 'invoice'

class InvoiceExportView(TemplateView):
    template_name = 'invoicing/invoice_export.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'csv':
            import csv
            from django.http import HttpResponse
            from apps.invoicing.models import Invoice
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="invoices.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Publisher', 'DRS', 'Status', 'Created'])
            for invoice in Invoice.objects.all():
                writer.writerow([
                    invoice.id,
                    str(invoice.publisher),
                    str(invoice.drs),
                    invoice.status,
                    invoice.created_at.strftime('%Y-%m-%d %H:%M')
                ])
            return response
        return super().get(request, *args, **kwargs)

class InvoicePDFView(DetailView):
    model = Invoice

    def get(self, request, *args, **kwargs):
        invoice = self.get_object()

        drs = invoice.drs
        invoice_lines = [{
            'description': getattr(drs, 'campaign_name', 'N/A'),
            'hsn_sac': '998365',  # or whatever is appropriate
            'qty': drs.publisher_conversions,
            'rate': drs.publisher_payout,
            # keep cgst/sgst in lines if you want per-line display
            'cgst_amount': invoice.gst_amount / 2 if invoice.gst_amount is not None else 0,
            'sgst_amount': invoice.gst_amount / 2 if invoice.gst_amount is not None else 0,
            'amount': drs.publisher_conversions * drs.publisher_payout,
        }]

        # Define cgst, sgst for use in template (for summary table)
        cgst = invoice.gst_amount / 2 if invoice.gst_amount is not None else 0
        sgst = invoice.gst_amount / 2 if invoice.gst_amount is not None else 0

        html = render_to_string(
            'invoicing/invoice_pdf_template.html',
            {
                'invoice': invoice,
                'invoice_lines': invoice_lines,
                'cgst': cgst,
                'sgst': sgst,
            }
        )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=invoice_{invoice.id}.pdf'
        weasyprint.HTML(string=html).write_pdf(response)
        return response
    
@method_decorator(login_required, name='dispatch')
class MyInvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/affiliate_invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        return Invoice.objects.filter(publisher=self.request.user.publisher)
# Create your views here.
