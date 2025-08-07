from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import DailyRevenueSheet
from .forms import DailyRevenueSheetForm
from django.http import JsonResponse
from apps.invoicing.models import CurrencyRate

class DailyRevenueSheetListView(ListView):
    model = DailyRevenueSheet
    template_name = 'drs/drs_list.html'
    context_object_name = 'drs_list'

class DailyRevenueSheetCreateView(CreateView):
    model = DailyRevenueSheet
    form_class = DailyRevenueSheetForm
    template_name = 'drs/drs_form.html'
    success_url = reverse_lazy('drs:drs_list')

class DailyRevenueSheetUpdateView(UpdateView):
    model = DailyRevenueSheet
    form_class = DailyRevenueSheetForm
    template_name = 'drs/drs_form.html'
    success_url = reverse_lazy('drs:drs_list')

class DailyRevenueSheetDeleteView(DeleteView):
    model = DailyRevenueSheet
    template_name = 'drs/drs_confirm_delete.html'
    success_url = reverse_lazy('drs:drs_list')

class DailyRevenueSheetDetailView(DetailView):
    model = DailyRevenueSheet
    template_name = 'drs/drs_detail.html'
    context_object_name = 'drs'
from django.views.generic import TemplateView

class DRSExportView(TemplateView):
    template_name = 'drs/drs_export.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'csv':
            import csv
            from django.http import HttpResponse
            from apps.drs.models import DailyRevenueSheet
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="drs.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Advertiser', 'Campaign Name', 'Affiliate', 'Start Date', 'End Date',
                'Adv Convs', 'Pub Convs', 'Rev/Conv', 'Payout/Conv', 'Revenue', 'Payout', 'Profit',
                'PID', 'af_prt', 'Account Manager', 'Updated'])
            for drs in DailyRevenueSheet.objects.all():
                writer.writerow([
                    drs.id, drs.advertiser, drs.campaign_name, drs.affiliate, drs.start_date, drs.end_date,
                    drs.advertiser_conversions, drs.publisher_conversions, drs.campaign_revenue, drs.publisher_payout,
                    drs.revenue, drs.payout, drs.profit, drs.pid, drs.af_prt, drs.account_manager, drs.updated_at
                ])
            return response
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drs_list'] = DailyRevenueSheet.objects.order_by('-updated_at')  # <= Add this line!
        return context
    
def drs_currency_amount_api(request):
    drs_id = request.GET.get('drs_id')
    currency = request.GET.get('currency', 'INR').upper()
    amount = 0
    if drs_id:
        try:
            drs = DailyRevenueSheet.objects.get(pk=drs_id)
            # This is your base amount in INR (edit the formula if needed!)
            base_inr_amount = float(drs.publisher_conversions) * float(drs.publisher_payout)
            if currency == 'INR':
                amount = base_inr_amount
            else:
                rate_obj = CurrencyRate.objects.filter(currency=currency).first()
                if rate_obj and rate_obj.rate_to_inr:
                    amount = round(base_inr_amount * float(rate_obj.rate_to_inr), 2)
                else:
                    amount = base_inr_amount  # fallback no conversion if missing
        except DailyRevenueSheet.DoesNotExist:
            pass
    return JsonResponse({'amount': f'{amount:.2f}'})

# Create your views here.
