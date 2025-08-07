from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Advertiser
from .forms import AdvertiserForm
from django.db.models import Count
from apps.offers.models import Offer
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from apps.offers.models import Offer

def advertiser_offers_ajax(request, advertiser_id):
    try:
        offers = Offer.objects.filter(advertiser_id=advertiser_id)
        html = render_to_string('advertisers/offer_list_fragment.html', {'offers': offers})
        return JsonResponse({'html': html})
    except Exception as e:
        return JsonResponse({'html': f'<div style="color:red">Django error: {str(e)}</div>'}, status=500)

class AdvertiserListView(ListView):
    model = Advertiser
    template_name = 'advertisers/advertiser_list.html'
    context_object_name = 'advertisers'

    def get_queryset(self):
        return Advertiser.objects.annotate(offers_count=Count('offers'))

class AdvertiserCreateView(CreateView):
    model = Advertiser
    form_class = AdvertiserForm
    template_name = 'advertisers/advertiser_form.html'
    success_url = reverse_lazy('advertisers:advertiser_list')

class AdvertiserUpdateView(UpdateView):
    model = Advertiser
    form_class = AdvertiserForm
    template_name = 'advertisers/advertiser_form.html'
    success_url = reverse_lazy('advertisers:advertiser_list')

class AdvertiserDeleteView(DeleteView):
    model = Advertiser
    template_name = 'advertisers/advertiser_confirm_delete.html'
    success_url = reverse_lazy('advertisers:list')

class AdvertiserDetailView(DetailView):
    model = Advertiser
    template_name = 'advertisers/advertiser_detail.html'
    context_object_name = 'advertiser'

class AdvertiserOfferUploadView(TemplateView):
    template_name = 'advertisers/offer_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['advertisers'] = Advertiser.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        import csv
        advertiser_id = request.POST.get('advertiser')
        advertiser = None
        if advertiser_id:
            advertiser = get_object_or_404(Advertiser, id=advertiser_id)
        try:
            # Handle file upload
            offer_file = request.FILES.get('offer_file')
            if offer_file:
                if offer_file.name.endswith('.csv') or offer_file.name.endswith('.xls'):
                    decoded_file = offer_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    count = 0
                    for row in reader:
                        Offer.objects.create(
                            advertiser=advertiser,
                            campaign_name=row.get('Campaign Name'),
                            geo=row.get('Geo'),
                            mmp=row.get('MMP', ''),
                            payout=row.get('Payout', 0) or 0,
                            payable_event=row.get('Payable Event', ''),
                            model=row.get('Model', ''),
                            category=row.get('Category', ''),
                            title=row.get('Campaign Name')
                        )
                        count += 1
                    messages.success(request, f"Successfully uploaded {count} offers from CSV.")
                else:
                    messages.error(request, "Only CSV files are supported at this time.")
            # Handle manual entry
            elif request.POST.get('campaign_name') and request.POST.get('geo'):
                Offer.objects.create(
                    advertiser=advertiser,
                    campaign_name=request.POST['campaign_name'],
                    geo=request.POST['geo'],
                    mmp=request.POST.get('mmp', ''),
                    payout=request.POST.get('payout', 0) or 0,
                    payable_event=request.POST.get('payable_event', ''),
                    model=request.POST.get('model', ''),
                    category=request.POST.get('category', ''),
                    title=request.POST['campaign_name'],
                )
                messages.success(request, "Offer added successfully.")
            else:
                messages.error(request, "Please select advertiser and fill all manual fields.")
        except Exception as e:
            messages.error(request, f"Error processing upload: {str(e)}")
        return self.get(request, *args, **kwargs)
