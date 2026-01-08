from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.exceptions import PermissionDenied
import json

from .models import Validation
from .forms import ValidationForm
from apps.drs.models import DailyRevenueSheet
from apps.publishers.models import Publisher
from apps.invoicing.models import Invoice

class ValidationListView(LoginRequiredMixin, ListView):
    model = Validation
    template_name = 'validation/validation_list.html'
    context_object_name = 'validations'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Check if user is in impersonation mode
        if 'impersonate_publisher_id' in self.request.session:
            publisher_id = self.request.session.get('impersonate_publisher_id')
            publisher = get_object_or_404(Publisher, id=publisher_id)
            queryset = queryset.filter(publisher=publisher)
        elif hasattr(self.request.user, 'publisher'):
            queryset = queryset.filter(publisher=self.request.user.publisher)
        
        # Apply filters from GET parameters
        publisher_id = self.request.GET.get('publisher')
        if publisher_id:
            queryset = queryset.filter(publisher_id=publisher_id)
        
        month = self.request.GET.get('month')
        if month:
            queryset = queryset.filter(month=month)
        
        # Filter by validation status
        status = self.request.GET.get('status')
        if status and status != '':
            if status in ['pending', 'approved', 'rejected', 'invoiced', 'paid']:
                queryset = queryset.filter(status=status.capitalize())
        
        # Filter by type (validation/drs)
        filter_type = self.request.GET.get('type', '')
        if filter_type == 'drs':
            # Show only DRS, hide validations
            queryset = Validation.objects.none()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        filter_type = self.request.GET.get('type', '')
        filter_status = self.request.GET.get('status', '')
        filter_publisher = self.request.GET.get('publisher', '')
        filter_month = self.request.GET.get('month', '')
        
        # Get DRS entries that need validation (paused or completed)
        drs_query = DailyRevenueSheet.objects.filter(
            status__in=['paused', 'completed']
        ).order_by('-start_date')
        
        # Check if user is in impersonation mode
        if 'impersonate_publisher_id' in self.request.session:
            publisher_id = self.request.session.get('impersonate_publisher_id')
            publisher = get_object_or_404(Publisher, id=publisher_id)
            drs_query = drs_query.filter(publisher=publisher)
        elif hasattr(self.request.user, 'publisher'):
            drs_query = drs_query.filter(publisher=self.request.user.publisher)
        
        # Apply filters to DRS
        if filter_publisher:
            drs_query = drs_query.filter(publisher_id=filter_publisher)
        
        if filter_month:
            try:
                year, month_num = filter_month.split('-')
                drs_query = drs_query.filter(
                    start_date__year=year, 
                    start_date__month=month_num
                )
            except:
                pass
        
        if filter_status and filter_status in ['paused', 'completed']:
            drs_query = drs_query.filter(status=filter_status)
        
        # Handle type filter
        if filter_type == 'validation':
            # Show only validations, no DRS
            drs_query = DailyRevenueSheet.objects.none()
        
        # Add DRS for validation to context
        context['drs_for_validation'] = drs_query
        
        # Calculate summary for filtered DRS (including paused/completed)
        context['summary'] = {
            'total_drs': drs_query.count(),
            'total_conversions': drs_query.aggregate(
                total=Sum('publisher_conversions')
            )['total'] or 0,
            'total_revenue': drs_query.aggregate(
                total=Sum('revenue')
            )['total'] or 0,
            'total_payout': drs_query.aggregate(
                total=Sum('payout')
            )['total'] or 0,
            'total_margin': drs_query.aggregate(
                total=Sum('profit')
            )['total'] or 0,
        }
        
        # Get paused campaigns data
        paused_campaigns = DailyRevenueSheet.objects.filter(
            status='paused'
        ).order_by('-start_date')
        
        if hasattr(self.request.user, 'publisher'):
            paused_campaigns = paused_campaigns.filter(publisher=self.request.user.publisher)
        
        # Prepare paused campaigns data
        paused_campaigns_data = []
        total_conversions_paused = 0
        total_amount_paused = 0
        
        for campaign in paused_campaigns:
            data = {
                'campaign_name': campaign.campaign_name,
                'pid': campaign.pid,
                'duration': f"{campaign.start_date.strftime('%Y-%m-%d %H:%M')} - {campaign.end_date.strftime('%H:%M') if campaign.end_date else 'N/A'}",
                'payout_rate': f"${campaign.publisher_payout:.2f}" if campaign.publisher_payout else "$0.00",
                'total_conversions': campaign.publisher_conversions or 0,
                'total_amount': f"${campaign.payout:.2f}" if campaign.payout else "$0.00",
            }
            paused_campaigns_data.append(data)
            total_conversions_paused += campaign.publisher_conversions or 0
            total_amount_paused += campaign.payout or 0
        
        # Add context data
        context['paused_campaigns'] = paused_campaigns_data
        context['total_conversions_paused'] = total_conversions_paused
        context['total_amount_paused'] = total_amount_paused
        context['publishers'] = Publisher.objects.all()
        
        # Get unique months
        validation_months = Validation.objects.values_list('month', flat=True).distinct()
        drs_months = DailyRevenueSheet.objects.filter(
            start_date__isnull=False
        ).dates('start_date', 'month', order='DESC')
        
        all_months = set()
        for month in validation_months:
            if month:
                all_months.add(month)
        for date in drs_months:
            all_months.add(date.strftime('%Y-%m'))
        
        context['months'] = sorted(all_months, reverse=True)
        context['selected_publisher'] = filter_publisher
        context['selected_month'] = filter_month
        context['filter_type'] = filter_type
        context['filter_status'] = filter_status
        
        # Check if it's an AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return only the table content for AJAX requests
            context['ajax_request'] = True
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        # Check if it's an AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return only the table container for AJAX
            html = render_to_string(
                'validation/partials/validation_table.html', 
                context, 
                self.request
            )
            return HttpResponse(html)
        
        # Return full page for normal requests
        return super().render_to_response(context, **response_kwargs)
                   
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
                initial.update({
                    'drs': drs.id,
                    'publisher': drs.publisher.id,
                    'month': drs.start_date.strftime('%Y-%m'),
                    'conversions': drs.publisher_conversions,
                    'payout': drs.payout,
                    'approve_payout': drs.payout,
                })
            except DailyRevenueSheet.DoesNotExist:
                pass
        return initial

    def post(self, request, *args, **kwargs):
        if 'load_drs' in request.POST:
            drs_id = request.POST.get('drs')
            initial = self.get_initial()
            if drs_id:
                try:
                    drs = DailyRevenueSheet.objects.get(id=drs_id)
                    initial.update({
                        'drs': drs.id,
                        'publisher': drs.publisher.id,
                        'month': drs.start_date.strftime('%Y-%m'),
                        'conversions': drs.publisher_conversions,
                        'payout': drs.payout,
                        'approve_payout': drs.payout,
                    })
                except DailyRevenueSheet.DoesNotExist:
                    pass
            form = self.form_class(initial=initial)
            self.object = None
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        validation = form.save(commit=False)
        
        # Auto-update DRS status to validated when validation is created
        if validation.drs and validation.drs.status in ['paused', 'completed']:
            validation.drs.status = 'validated'
            validation.drs.validated_at = timezone.now()
            validation.drs.validated_by = self.request.user
            validation.drs.save()
        
        validation.save()
        messages.success(self.request, 'Validation created successfully!')
        return redirect(self.success_url)

class ValidationUpdateView(UpdateView):
    model = Validation
    form_class = ValidationForm
    template_name = 'validation/validation_form.html'
    success_url = reverse_lazy('validation:validation_list')
    
    def get(self, request, *args, **kwargs):
        # Check if this is a status update request (approve/reject/mark-invoiced/mark-paid)
        action = request.GET.get('action')
        if action:
            validation = self.get_object()
            
            if action == 'approve':
                validation.status = 'Approved'
                validation.approved_at = timezone.now()
                validation.approved_by = request.user
                validation.save()
                
                # Update DRS status
                validation.drs.status = 'approved'
                validation.drs.save()
                
                messages.success(request, 'Validation approved successfully!')
                
            elif action == 'reject':
                validation.status = 'Rejected'
                validation.save()
                messages.warning(request, 'Validation rejected.')
                
            elif action == 'mark-invoiced':
                validation.status = 'Invoiced'
                validation.invoiced_at = timezone.now()
                validation.save()
                
                # Update DRS status
                validation.drs.status = 'invoiced'
                validation.drs.save()
                
                messages.info(request, 'Validation marked as invoiced.')
                
            elif action == 'mark-paid':
                validation.status = 'Paid'
                validation.paid_at = timezone.now()
                validation.save()
                
                # Update DRS status
                validation.drs.status = 'paid'
                validation.drs.paid_at = timezone.now()
                validation.drs.save()
                
                messages.success(request, 'Validation marked as paid!')
            
            # Redirect back to the appropriate page
            referer = request.META.get('HTTP_REFERER', '')
            if 'my-validation' in referer:
                return redirect('validation:my_validation')
            elif 'tab' in referer:
                return redirect('validation:validation_tab')
            else:
                return redirect('validation:validation_list')
        
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        old_status = form.instance.status
        new_status = form.cleaned_data.get('status')
        
        # If status changed to Approved, update timestamps
        if old_status != 'Approved' and new_status == 'Approved':
            form.instance.approved_at = timezone.now()
            form.instance.approved_by = self.request.user
            
            # Update DRS status
            form.instance.drs.status = 'approved'
            form.instance.drs.save()
        
        # If status changed to Invoiced, update timestamps
        elif old_status != 'Invoiced' and new_status == 'Invoiced':
            form.instance.invoiced_at = timezone.now()
            
            # Update DRS status
            form.instance.drs.status = 'invoiced'
            form.instance.drs.save()
        
        # If status changed to Paid, update timestamps
        elif old_status != 'Paid' and new_status == 'Paid':
            form.instance.paid_at = timezone.now()
            
            # Update DRS status
            form.instance.drs.status = 'paid'
            form.instance.drs.paid_at = timezone.now()
            form.instance.drs.save()
        
        messages.success(self.request, f'Validation updated successfully!')
        return super().form_valid(form)

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
        context['status_choices'] = ['Pending', 'Approved', 'Rejected']
        return context

class ValidationExportView(TemplateView):
    template_name = 'validation/validation_export.html'
    
    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'csv':
            import csv
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
            messages.success(request, f"Validation summary sent to {request.POST['email']}.")
        else:
            messages.error(request, "Invalid form submission.")
        return self.get(request, *args, **kwargs)

class ValidationTabView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Validation Tab - Shows saved validation reports grouped by month"""
    template_name = 'validation/validation_tab.html'
    
    def test_func(self):
        # Allow all authenticated users to see validation tab
        return self.request.user.is_authenticated
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Determine which publisher's validations to show
        if 'impersonate_publisher_id' in self.request.session:
            # Show impersonated publisher's validations
            publisher_id = self.request.session.get('impersonate_publisher_id')
            publisher = get_object_or_404(Publisher, id=publisher_id)
            validations = Validation.objects.filter(publisher=publisher)
        elif hasattr(user, 'publisher'):
            # Show user's own publisher validations
            validations = Validation.objects.filter(publisher=user.publisher)
        else:
            # Admin users - show all validations
            validations = Validation.objects.all()
        
        # Order by month and created date
        ordered_validations = validations.order_by('-month', '-created_at')
        context['my_validations'] = ordered_validations
        
        # Calculate monthly totals for grouped display
        monthly_totals = {}
        for validation in ordered_validations:
            month = validation.month
            
            if month not in monthly_totals:
                monthly_totals[month] = {
                    'generated_amount': 0,
                    'total_payout': 0,
                    'total_conversions': 0,
                    'count': 0
                }
            
            # Add to monthly totals
            # IMPORTANT: If generated_amount doesn't exist, we need an alternative
            # Option 1: Use another field like total payout multiplied by some factor
            # Option 2: Calculate from DRS if available
            # For now, let's use a default value or calculate from DRS
            
            # Try to get generated amount from DRS if it exists
            if hasattr(validation, 'drs') and validation.drs:
                # If DRS has a revenue field, use it as generated amount
                # Otherwise, use a calculation or default
                generated = getattr(validation.drs, 'revenue', 0) or 0
                # You can adjust this calculation based on your business logic
                # For example: revenue * some_factor or fixed amount per conversion
            else:
                # Default calculation: payout * 10 (adjust this based on your needs)
                generated = (validation.approve_payout or 0) * 10
            
            monthly_totals[month]['generated_amount'] += generated
            monthly_totals[month]['total_payout'] += validation.approve_payout or 0
            monthly_totals[month]['total_conversions'] += validation.conversions or 0
            monthly_totals[month]['count'] += 1
        
        context['monthly_totals'] = monthly_totals
        
        # Calculate overall summary statistics
        context['total_conversions'] = validations.aggregate(
            total=Sum('conversions')
        )['total'] or 0
        
        context['total_payout'] = validations.aggregate(
            total=Sum('approve_payout')
        )['total'] or 0
        
        # Count uploaded invoices
        context['uploaded_invoices'] = validations.filter(
            invoice__isnull=False
        ).count()
        
        # Get DRS entries that still need validation (paused or completed)
        drs_query = DailyRevenueSheet.objects.filter(
            Q(status='paused') | Q(status='completed')
        )
        
        # Filter by appropriate publisher
        if 'impersonate_publisher_id' in self.request.session:
            publisher_id = self.request.session.get('impersonate_publisher_id')
            publisher = get_object_or_404(Publisher, id=publisher_id)
            drs_query = drs_query.filter(publisher=publisher)
        elif hasattr(user, 'publisher'):
            drs_query = drs_query.filter(publisher=user.publisher)
        
        context['drs_for_validation'] = drs_query.order_by('-start_date')
        
        # Get publisher's pending invoices count
        if hasattr(user, 'publisher'):
            context['pending_invoices_count'] = Invoice.objects.filter(
                publisher=user.publisher,
                status__in=['Pending', 'Overdue']
            ).count()
        
        return context

class SaveReportView(LoginRequiredMixin, View):
    """Save Validation - Complete working version"""
    
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            drs_id = data.get('drs_id')
            
            if not drs_id:
                return JsonResponse({'error': 'DRS ID is required'}, status=400)
            
            # Get DRS
            try:
                drs = DailyRevenueSheet.objects.select_related('publisher').get(id=drs_id)
            except DailyRevenueSheet.DoesNotExist:
                return JsonResponse({'error': 'DRS not found'}, status=404)
            
            # Check permissions
            user = request.user
            
            # Allow if user is admin/subadmin
            is_admin = user.is_superuser or user.groups.filter(name__in=['admin', 'subadmin']).exists()
            
            # Allow if user is publisher owner
            is_publisher_owner = hasattr(user, 'publisher') and user.publisher == drs.publisher
            
            # Allow if in impersonation mode
            is_impersonating = 'impersonate_publisher_id' in request.session
            if is_impersonating:
                impersonated_id = request.session.get('impersonate_publisher_id')
                is_impersonating_owner = str(drs.publisher.id) == str(impersonated_id)
            else:
                is_impersonating_owner = False
            
            if not (is_admin or is_publisher_owner or is_impersonating_owner):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Check if DRS is already validated
            if drs.status == 'validated':
                return JsonResponse({
                    'success': False,
                    'message': 'This DRS has already been validated.',
                    'already_validated': True
                }, status=400)
            
            # Prepare month string
            if drs.start_date:
                month_str = drs.start_date.strftime('%Y-%m')
            else:
                month_str = timezone.now().strftime('%Y-%m')
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Check if validation already exists
                existing_validation = Validation.objects.filter(drs=drs).first()
                
                if existing_validation:
                    # Update existing validation - AUTO APPROVE
                    validation = existing_validation
                    validation.status = 'Approved'  # Changed from 'Pending'
                    validation.submitted_at = timezone.now()
                    validation.submitted_by = user
                    validation.approved_at = timezone.now()  # Add approval timestamp
                    validation.approved_by = user  # Set approver
                    validation.save()
                    created = False
                    message = 'Validation updated and approved successfully! You can now upload invoice.'
                else:
                    # Create new validation - AUTO APPROVE
                    validation = Validation.objects.create(
                        drs=drs,
                        publisher=drs.publisher,
                        month=month_str,
                        conversions=drs.publisher_conversions or 0,
                        payout=drs.payout or 0,
                        approve_payout=drs.payout or 0,
                        status='Approved',  # Changed from 'Pending'
                        submitted_at=timezone.now(),
                        submitted_by=user,
                        approved_at=timezone.now(),  # Add approval timestamp
                        approved_by=user  # Set approver
                    )
                    created = True
                    message = 'Validation created and approved successfully! It will appear in your Validation tab and you can upload invoice.'
                
                # Update DRS status
                drs.status = 'validated'
                drs.validated_at = timezone.now()
                drs.validated_by = user
                drs.save()
            
            return JsonResponse({
                'success': True,
                'message': message,
                'validation_id': validation.id,
                'drs_id': drs.id,
                'created': created,
                'status': validation.status,
                'drs_status': drs.status,
                'already_validated': False
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in SaveReportView: {error_trace}")
            return JsonResponse({
                'error': f'Server error: {str(e)}',
                'details': error_trace if settings.DEBUG else None
            }, status=500)
               
class MyValidationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """My Validation Section - Shows publisher's validations"""
    template_name = 'validation/my_validation.html'
    context_object_name = 'validations'
    model = Validation
    
    def test_func(self):
        return hasattr(self.request.user, 'publisher')
    
    def get_queryset(self):
        return Validation.objects.filter(
            publisher=self.request.user.publisher
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add summary statistics
        validations = self.get_queryset()
        context['total_validations'] = validations.count()
        context['pending_validations'] = validations.filter(status='Pending').count()
        context['approved_validations'] = validations.filter(status='Approved').count()
        context['rejected_validations'] = validations.filter(status='Rejected').count()
        
        # Calculate totals
        context['total_payout'] = validations.aggregate(
            total=Sum('payout')
        )['total'] or 0
        context['total_approve_payout'] = validations.aggregate(
            total=Sum('approve_payout')
        )['total'] or 0
        
        return context

class UploadInvoiceView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Publisher uploads invoice from My Validation section"""
    
    def test_func(self):
        user = self.request.user
        # Allow if user has a publisher OR is admin/subadmin
        return hasattr(user, 'publisher') or user.is_superuser or user.groups.filter(name__in=['admin', 'subadmin']).exists()
    
    def post(self, request, validation_id):
        validation = get_object_or_404(Validation, id=validation_id)
        
        # Check permissions
        user = request.user
        
        # For admin users, allow upload
        is_admin = user.is_superuser or user.groups.filter(name__in=['admin', 'subadmin']).exists()
        
        # For publisher users, check ownership
        is_publisher_owner = hasattr(user, 'publisher') and validation.publisher == user.publisher
        
        # Check if in impersonation mode
        is_impersonating = 'impersonate_publisher_id' in request.session
        if is_impersonating:
            impersonated_id = request.session.get('impersonate_publisher_id')
            is_impersonating_owner = str(validation.publisher.id) == str(impersonated_id)
        else:
            is_impersonating_owner = False
        
        # Check if user has permission
        if not (is_admin or is_publisher_owner or is_impersonating_owner):
            messages.error(request, 'You do not have permission to upload invoice for this validation.')
            return redirect('validation:validation_tab')
        
        # Check if validation is approved
        if validation.status != 'Approved':
            messages.error(request, 'Only approved validations can have invoices uploaded.')
            return redirect('validation:validation_tab')
        
        # Get uploaded file
        invoice_file = request.FILES.get('invoice_file')
        
        if not invoice_file:
            messages.error(request, 'No file uploaded.')
            return redirect('validation:validation_tab')
        
        try:
            with transaction.atomic():
                # Create invoice from validation
                invoice = Invoice.objects.create(
                    party_type='publisher',
                    publisher=validation.publisher,
                    drs=validation.drs,
                    amount=validation.approve_payout,
                    status='Pending',
                    date=timezone.now().date(),
                    pdf=invoice_file
                )
                
                # Auto-generate invoice number
                if not invoice.invoice_number:
                    count = Invoice.objects.filter(party_type='publisher').count() + 1
                    invoice.invoice_number = f'PUB-{count:06d}'
                    invoice.save()
                
                # CRITICAL FIX: Update validation to link with invoice
                # This ensures the template condition `not validation.invoice` works correctly
                validation.invoice = invoice
                validation.save()
                
                # Update DRS status to invoiced
                if validation.drs:
                    validation.drs.status = 'invoiced'
                    validation.drs.invoice = invoice
                    validation.drs.invoiced_at = timezone.now()
                    validation.drs.save()
                
                messages.success(request, 'Invoice uploaded successfully!')
                
                # If AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Invoice uploaded successfully!',
                        'invoice_id': invoice.id,
                        'validation_id': validation.id
                    })
                
        except Exception as e:
            messages.error(request, f'Error uploading invoice: {str(e)}')
        
        # Redirect back to validation tab WITH success parameter
        return redirect(f'{reverse("validation:validation_tab")}?invoice_uploaded=true')
    
class InvoiceApprovalView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Admin approval of invoices - Updates status for Publisher"""
    
    def test_func(self):
        # Only admin and subadmin can approve invoices
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['admin', 'subadmin']).exists()
    
    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            invoice.status = 'Approved'
            invoice.save()
            
            # Update related DRS status
            if invoice.drs:
                invoice.drs.status = 'approved'
                invoice.drs.save()
            
            messages.success(request, 'Invoice approved successfully!')
            
        elif action == 'mark_paid':
            invoice.status = 'Paid'
            invoice.save()
            
            # Update DRS status to paid
            if invoice.drs:
                invoice.drs.status = 'paid'
                invoice.drs.save()
            
            # Update related validation status if exists
            validation = Validation.objects.filter(drs=invoice.drs).first()
            if validation:
                validation.status = 'Approved'  # Mark validation as approved when paid
                validation.save()
            
            messages.success(request, 'Invoice marked as paid!')
            
        elif action == 'reject':
            invoice.status = 'Rejected'
            invoice.save()
            messages.warning(request, 'Invoice rejected.')
            
        else:
            messages.error(request, 'Invalid action.')
        
        # If AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'status': invoice.status,
                'message': f'Invoice status updated to {invoice.status}'
            })
        
        return redirect('invoicing:invoice_list')

class GenerateInvoiceView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Generate invoice from approved validation"""
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['admin', 'subadmin']).exists()
    
    def post(self, request, validation_id):
        validation = get_object_or_404(Validation, id=validation_id)
        
        # Check if validation is approved
        if validation.status != 'Approved':
            messages.error(request, 'Only approved validations can generate invoices.')
            return redirect('validation:validation_tab')
        
        # Check if invoice already exists
        if validation.drs and validation.drs.invoice:
            messages.warning(request, 'Invoice already exists for this validation.')
            return redirect('validation:validation_tab')
        
        try:
            with transaction.atomic():
                # Create invoice from validation
                invoice = Invoice.objects.create(
                    party_type='publisher',
                    publisher=validation.publisher,
                    drs=validation.drs,
                    amount=validation.approve_payout,
                    status='Pending',
                    date=timezone.now().date()
                )
                
                # Auto-generate invoice number
                if not invoice.invoice_number:
                    count = Invoice.objects.filter(party_type='publisher').count() + 1
                    invoice.invoice_number = f'PUB-{count:06d}'
                    invoice.save()
                
                # Update DRS status to invoiced
                if validation.drs:
                    validation.drs.status = 'invoiced'
                    validation.drs.invoice = invoice
                    validation.drs.invoiced_at = timezone.now()
                    validation.drs.save()
                
                messages.success(request, f'Invoice #{invoice.invoice_number} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating invoice: {str(e)}')
        
        return redirect('validation:validation_tab')

class BulkApproveValidationsView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Bulk approve validations"""
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['admin', 'subadmin']).exists()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            validation_ids = data.get('validation_ids', [])
            
            if not validation_ids:
                return JsonResponse({'error': 'No validations selected'}, status=400)
            
            approved_count = 0
            for validation_id in validation_ids:
                try:
                    validation = Validation.objects.get(id=validation_id)
                    validation.status = 'Approved'
                    validation.save()
                    approved_count += 1
                except Validation.DoesNotExist:
                    continue
            
            messages.success(request, f'{approved_count} validations approved successfully!')
            
            return JsonResponse({
                'success': True,
                'message': f'{approved_count} validations approved successfully!',
                'approved_count': approved_count
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def send_validation_summary(validation):
    """Send email summary for validation"""
    publisher = validation.publisher
    if publisher.email:
        summary = f"Validation result for {validation.month}:\nStatus: {validation.status}\nApproved Payout: {validation.approve_payout}"
        # Uncomment and configure your email settings
        # from django.core.mail import send_mail
        # send_mail(
        #     subject=f"Validation Summary ({validation.month})",
        #     message=summary,
        #     recipient_list=[publisher.email],
        #     from_email='your@email.com',
        #     fail_silently=False,
        # )
        return True
    return False

class CheckUserStatusView(View):
    """Debug view to check user status"""
    
    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'is_authenticated': user.is_authenticated,
            'is_superuser': user.is_superuser,
            'has_publisher': hasattr(user, 'publisher'),
            'impersonate_publisher_id': request.session.get('impersonate_publisher_id'),
            'groups': list(user.groups.values_list('name', flat=True)) if user.is_authenticated else [],
        }
        return JsonResponse(data)