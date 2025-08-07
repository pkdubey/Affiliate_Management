from django.shortcuts import render
# models for validation app
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Validation
from .forms import ValidationForm
from django.core.mail import send_mail
from django.views.generic import TemplateView
from apps.drs.models import DailyRevenueSheet

class ValidationListView(ListView):
    model = Validation
    template_name = 'validation/validation_list.html'
    context_object_name = 'validations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.publishers.models import Publisher
        from apps.drs.models import DailyRevenueSheet
        context['publishers'] = Publisher.objects.all()
        # collect yyyy-mm from start_date in DRS
        context['months'] = sorted({d.strftime('%Y-%m') for d in DailyRevenueSheet.objects.values_list('start_date', flat=True)})
        context['selected_publisher'] = self.request.GET.get('publisher', '')
        context['selected_month'] = self.request.GET.get('month', '')
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.publishers.models import Publisher
        from apps.drs.models import DailyRevenueSheet
        context['publishers'] = Publisher.objects.all()
        # Months present in DRS table, for dropdown
        context['months'] = (
            DailyRevenueSheet.objects.values_list('start_date', flat=True)
            .distinct()
        )
        # For month dropdown as 'YYYY-MM' or similar:
        context['months'] = sorted({d.strftime('%Y-%m') for d in context['months']})
        context['selected_publisher'] = self.request.GET.get('publisher', '')
        context['selected_month'] = self.request.GET.get('month', '')
        return context

class ValidationCreateView(CreateView):
    model = Validation
    form_class = ValidationForm
    template_name = 'validation/validation_form.html'
    success_url = reverse_lazy('validation:validation_list')

    def get_initial(self):
        initial = super().get_initial()
        drs_id = self.request.GET.get('drs')
        if drs_id:
            try:
                drs = DailyRevenueSheet.objects.get(id=drs_id)
                initial.update({...})
            except DailyRevenueSheet.DoesNotExist:
                pass
        return initial

    def post(self, request, *args, **kwargs):
        if 'load_drs' in request.POST:
            drs_id = request.POST.get('drs')
            initial = self.get_initial()    # dict of initial values
            if drs_id:
                try:
                    drs = DailyRevenueSheet.objects.get(id=drs_id)
                    initial.update({
                        'drs': drs.id,
                        'publisher': drs.affiliate_id,
                        'month': drs.start_date.strftime('%Y-%m'),
                        'conversions': drs.publisher_conversions,
                        'payout': drs.publisher_payout,
                        'approve_payout': drs.publisher_payout,
                    })
                except DailyRevenueSheet.DoesNotExist:
                    pass
            form = self.form_class(initial=initial)
            # The crucial fix:
            self.object = None
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return super().post(request, *args, **kwargs)

class ValidationUpdateView(UpdateView):
    model = Validation
    form_class = ValidationForm
    template_name = 'validation/validation_form.html'
    success_url = reverse_lazy('validation:validation_list')

class ValidationDeleteView(DeleteView):
    model = Validation
    template_name = 'validation/validation_confirm_delete.html'
    success_url = reverse_lazy('validation:validation_list')

class ValidationDetailView(DetailView):
    model = Validation
    template_name = 'validation/validation_detail.html'
    context_object_name = 'validation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        v = self.object
        context['table'] = {
            'Campaign Name': v.drs.campaign_name,
            'Publisher': v.publisher.company_name,
            'PID': v.drs.pid,
            'Conversions': v.conversions,
            'Payout': v.payout,
            'Approve Payout': v.approve_payout,
            'Status': v.status,
        }
        context['affiliate_email'] = getattr(v.publisher, 'email', None)
        context['status_choices'] = ['Pending', 'Approved', 'Rejected']  # <-- ADD THIS
        return context

class ValidationExportView(TemplateView):
    template_name = 'validation/validation_export.html'
    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'csv':
            import csv
            from django.http import HttpResponse
            publisher_id = request.GET.get('publisher')
            month = request.GET.get('month')
            qs = Validation.objects.all()
            if publisher_id:
                qs = qs.filter(publisher_id=publisher_id)
            if month:
                qs = qs.filter(month=month)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="validations.csv"'
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Campaign Name', 'Publisher', 'PID', 'Month', 'Conversions', 'Payout', 'Approve Payout', 'Status'
            ])
            for v in qs:
                writer.writerow([
                    v.id,
                    v.drs.campaign_name,
                    v.publisher.company_name,
                    v.drs.pid,
                    v.month,
                    v.conversions,
                    v.payout,
                    v.approve_payout,
                    v.status
                ])
            return response
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from apps.validation.models import Validation
        # Status update
        if request.POST.get('validation_id') and request.POST.get('status'):
            try:
                validation = Validation.objects.get(id=request.POST['validation_id'])
                validation.status = request.POST['status']
                validation.save()
                messages.success(request, f"Validation status updated to {validation.status}.")
            except Validation.DoesNotExist:
                messages.error(request, "Validation record not found.")
        # Email summary
        elif request.POST.get('send_email') and request.POST.get('email'):
            # Simulate sending email (replace with actual email logic)
            messages.success(request, f"Validation summary sent to {request.POST['email']}.")
        else:
            messages.error(request, "Invalid form submission.")
        return self.get(request, *args, **kwargs)

def send_validation_summary(validation):
    publisher = validation.publisher
    if publisher.email:
        summary = f"Validation result for {validation.month}:\nStatus: {validation.status}\nApproved Payout: {validation.approve_payout}"
        send_mail(
            subject=f"Validation Summary ({validation.month})",
            message=summary,
            recipient_list=[publisher.email],
            from_email='your@email.com',
            fail_silently=False,
        )
        return True
    return False
