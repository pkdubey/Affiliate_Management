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
from django.views import View


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/invoice_list.html'
    context_object_name = 'invoices'


    def get_queryset(self):
        party_type = self.request.GET.get('tab', 'advertiser')
        status = self.request.GET.get('status')
        client = self.request.GET.get('client')
        month = self.request.GET.get('month')
        queryset = Invoice.objects.all()
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
        return queryset

    def get_context_data(self, **kwargs):
        from apps.advertisers.models import Advertiser
        from apps.publishers.models import Publisher
        import calendar
        context = super().get_context_data(**kwargs)
        active_tab = self.request.GET.get('tab', 'advertiser')
        context['active_tab'] = active_tab
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_client'] = self.request.GET.get('client', '')
        context['selected_month'] = self.request.GET.get('month', '')
        if active_tab == 'advertiser':
            context['clients'] = Advertiser.objects.all()
        else:
            context['clients'] = Publisher.objects.all()
        context['months'] = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        return context

class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'
    success_url = reverse_lazy('invoicing:invoice_list')

    def get_initial(self):
        import contextlib
        initial = super().get_initial()
        if drs_id := self.request.GET.get('drs'):
            with contextlib.suppress(Exception):
                from apps.drs.models import DailyRevenueSheet
                drs = DailyRevenueSheet.objects.get(id=drs_id)
                initial.update({
                    'drs': drs.id,
                    'currency': 'INR',
                    'amount': drs.publisher_payout,
                })
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
        if request.GET.get('export') != 'csv':
            return super().get(request, *args, **kwargs)
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

class InvoicePDFView(View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        html = render_to_string('invoicing/invoice_pdf.html', {'invoice': invoice})
        pdf = weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="invoice_{invoice.invoice_number}.pdf"'
        return response
    
@method_decorator(login_required, name='dispatch')
class MyInvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/affiliate_invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        return Invoice.objects.filter(publisher=self.request.user.publisher)
# Create your views here.
