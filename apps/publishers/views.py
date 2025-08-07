from django.shortcuts import render
from django.db.models import Count

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Publisher, Wishlist
from .forms import PublisherForm
from django.http import JsonResponse
from django.template.loader import render_to_string

def publisher_wishlist_ajax(request, publisher_id):
    wishlist_qs = Wishlist.objects.filter(publisher_id=publisher_id)
    html = render_to_string('publishers/wishlist_list_fragment.html', {'wishlist_items': wishlist_qs})
    return JsonResponse({'html': html})

class PublisherListView(ListView):
    model = Publisher
    template_name = 'publishers/publisher_list.html'
    context_object_name = 'publishers'

    def get_queryset(self):
        return Publisher.objects.annotate(
            wishlist_count=Count('wishlists')
        )

class PublisherCreateView(CreateView):
    model = Publisher
    form_class = PublisherForm
    template_name = 'publishers/publisher_form.html'
    success_url = reverse_lazy('publishers:publisher_list')

class PublisherUpdateView(UpdateView):
    model = Publisher
    form_class = PublisherForm
    template_name = 'publishers/publisher_form.html'
    success_url = reverse_lazy('publishers:publisher_list')

class PublisherDeleteView(DeleteView):
    model = Publisher
    template_name = 'publishers/publisher_confirm_delete.html'
    success_url = reverse_lazy('publishers:list')

class PublisherDetailView(DetailView):
    model = Publisher
    template_name = 'publishers/publisher_detail.html'
    context_object_name = 'publisher'
from django.views.generic import TemplateView

class PublisherWishlistUploadView(TemplateView):
    template_name = 'publishers/wishlist_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publishers'] = Publisher.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        import csv
        publisher_id = request.POST.get('publisher')
        publisher = None
        if publisher_id:
            publisher = get_object_or_404(Publisher, id=publisher_id)

        try:
            # Handle file upload
            wishlist_file = request.FILES.get('wishlist_file')
            if wishlist_file:
                if wishlist_file.name.endswith('.csv'):
                    decoded_file = wishlist_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    count = 0
                    for row in reader:
                        Wishlist.objects.create(
                            publisher=publisher,
                            desired_campaign=row.get('Desired Campaign'),
                            geo=row.get('Geo'),
                            payout=row.get('Payout') or None,
                            payable_event=row.get('Payable Event') or '',
                            model=row.get('Model') or '',
                            category=row.get('Category') or ''
                        )
                        count += 1
                    messages.success(request, f"Successfully uploaded {count} wishlist offers from CSV.")
                else:
                    messages.error(request, "Only CSV files are supported at this time.")
            elif request.POST.get('desired_campaign') and request.POST.get('geo'):
                Wishlist.objects.create(
                    publisher=publisher,
                    desired_campaign=request.POST['desired_campaign'],
                    geo=request.POST['geo'],
                    payout=request.POST.get('payout') or None,
                    payable_event=request.POST.get('payable_event', ''),
                    model=request.POST.get('model', ''),
                    category=request.POST.get('category', ''),
                )
                messages.success(request, "Wishlist offer added successfully.")
            else:
                messages.error(request, "Please select a publisher and fill all manual fields.")
        except Exception as e:
            messages.error(request, f"Error processing upload: {str(e)}")
        return self.get(request, *args, **kwargs)

class PublisherPortalView(TemplateView):
    template_name = 'publishers/portal.html'

    def get(self, request, *args, **kwargs):
        from apps.invoicing.models import Invoice
        from apps.validation.models import Validation
        invoices = Invoice.objects.all()
        validations = Validation.objects.all()
        context = self.get_context_data(invoices=invoices, validations=validations)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from apps.invoicing.models import Invoice
        # Simulate invoice upload (add logic as needed)
        if request.FILES.get('invoice_file'):
            messages.success(request, "Invoice uploaded successfully.")
        else:
            messages.error(request, "Please select a file to upload.")
        return self.get(request, *args, **kwargs)

# Create your views here.
