from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from apps.advertisers.models import Advertiser
from apps.publishers.models import Publisher
from apps.offers.models import Offer
from apps.invoicing.models import Invoice
from django.db.models import Sum
from django.utils.timezone import now, timedelta
import json

# -- FULL ADMIN DASHBOARD (Admins/Subadmins Only)
@login_required
@role_required(['admin', 'subadmin'])
def dashboard_view(request):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # --- Global Metrics ---
    total_advertisers = Advertiser.objects.count()
    total_publishers = Publisher.objects.count()
    total_offers = Offer.objects.count()
    total_invoices = Invoice.objects.count()

    # --- Revenue & Invoice Statuses ---

    # Invoice status counts
    paid_invoices = Invoice.objects.filter(status='Paid').count()
    unpaid_invoices = Invoice.objects.filter(status='Pending').count()
    overdue_invoices = Invoice.objects.filter(status='Overdue').count()

    today_revenue = Invoice.objects.filter(created_at__date=today).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0
    week_revenue = Invoice.objects.filter(created_at__date__gte=start_of_week).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0
    month_revenue = Invoice.objects.filter(created_at__date__gte=start_of_month).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0

    # Ensure numbers are simple floats for templates
    today_revenue = float(today_revenue)
    week_revenue = float(week_revenue)
    month_revenue = float(month_revenue)

    # --- Graph Data (last 7 days) ---
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_revenue = Invoice.objects.filter(created_at__date=day).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0
        day_profit = Invoice.objects.filter(created_at__date=day).aggregate(total=Sum('drs__profit'))['total'] or 0
        daily_stats.append({'date': day.strftime('%Y-%m-%d'), 'revenue': float(day_revenue), 'profit': float(day_profit)})
    daily_stats.reverse()

    labels = [item['date'] for item in daily_stats]
    revenues = [item['revenue'] for item in daily_stats]
    profits = [item['profit'] for item in daily_stats]

    context = {
        'total_advertisers': total_advertisers,
        'total_publishers': total_publishers,
        'total_offers': total_offers,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'overdue_invoices': overdue_invoices,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'chart_labels': json.dumps(labels),
        'chart_revenues': json.dumps(revenues),
        'chart_profits': json.dumps(profits),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)

# -- PUBLISHER DASHBOARD (Publisher Only)
@login_required
@role_required(['publisher'])
def publisher_dashboard(request):
    print("=== PUBLISHER DASHBOARD VIEW ENTERED ===")
    print("User: {}".format(request.user.username))
    print("Role: {}".format(request.user.role))
    
    # Import models
    from apps.drs.models import DailyRevenueSheet
    from apps.validation.models import Validation
    
    user = request.user
    total_income = 0
    total_invoices = 0
    
    # Try different approaches to get the publisher's income
    try:
        # Option 1: If Invoice model has a user field
        if hasattr(Invoice, 'user'):
            invoice_filter = {'user': user}
            total_income = Invoice.objects.filter(**invoice_filter).aggregate(
                total=Sum('drs__campaign_revenue')
            )['total'] or 0
            total_invoices = Invoice.objects.filter(**invoice_filter).count()
        
        # Option 2: If Invoice model has a publisher field and user has publisher relation
        elif hasattr(Invoice, 'publisher') and hasattr(user, 'publisher'):
            invoice_filter = {'publisher': user.publisher}
            total_income = Invoice.objects.filter(**invoice_filter).aggregate(
                total=Sum('drs__campaign_revenue')
            )['total'] or 0
            total_invoices = Invoice.objects.filter(**invoice_filter).count()
        
        # Option 3: Directly from DRS if there's a user relation
        elif hasattr(DailyRevenueSheet, 'user'):
            total_income = DailyRevenueSheet.objects.filter(user=user).aggregate(
                total=Sum('campaign_revenue')
            )['total'] or 0
        
        # Option 4: Directly from DRS if there's a publisher relation
        elif hasattr(DailyRevenueSheet, 'publisher') and hasattr(user, 'publisher'):
            total_income = DailyRevenueSheet.objects.filter(publisher=user.publisher).aggregate(
                total=Sum('campaign_revenue')
            )['total'] or 0
        
        # Option 5: Fallback - get all DRS records (you might want to filter this better)
        else:
            total_income = DailyRevenueSheet.objects.aggregate(
                total=Sum('campaign_revenue')
            )['total'] or 0
            
    except Exception as e:
        print(f"Error calculating income: {e}")
        total_income = 0
        total_invoices = 0
    
    # Convert to float for template
    total_income = float(total_income)
    
    # Get today's date for revenue calculations
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    # Calculate daily, weekly, monthly revenue
    try:
        # Today's revenue - assuming DRS has a date field
        # If not, use created_at or start_date
        if hasattr(DailyRevenueSheet, 'date'):
            today_revenue = DailyRevenueSheet.objects.filter(
                date=today
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
            week_revenue = DailyRevenueSheet.objects.filter(
                date__gte=start_of_week
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
            month_revenue = DailyRevenueSheet.objects.filter(
                date__gte=start_of_month
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
        elif hasattr(DailyRevenueSheet, 'start_date'):
            today_revenue = DailyRevenueSheet.objects.filter(
                start_date=today
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
            week_revenue = DailyRevenueSheet.objects.filter(
                start_date__gte=start_of_week
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
            month_revenue = DailyRevenueSheet.objects.filter(
                start_date__gte=start_of_month
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
        elif hasattr(DailyRevenueSheet, 'created_at'):
            today_revenue = DailyRevenueSheet.objects.filter(
                created_at__date=today
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
            week_revenue = DailyRevenueSheet.objects.filter(
                created_at__date__gte=start_of_week
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
            month_revenue = DailyRevenueSheet.objects.filter(
                created_at__date__gte=start_of_month
            ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
            
        else:
            today_revenue = week_revenue = month_revenue = 0
            
    except Exception as e:
        print(f"Error calculating period revenue: {e}")
        today_revenue = week_revenue = month_revenue = 0
    
    # Convert to float
    today_revenue = float(today_revenue)
    week_revenue = float(week_revenue)
    month_revenue = float(month_revenue)
    
    # ====================================================
    # VALIDATION OVERVIEW CALCULATIONS
    # ====================================================
    try:
        # Get publisher object
        if hasattr(user, 'publisher'):
            publisher = user.publisher
            
            # 1. Pending validation count (DRS with status paused or completed)
            pending_validation_count = DailyRevenueSheet.objects.filter(
                publisher=publisher,
                status__in=['paused', 'completed']
            ).count()
            
            # 2. Submitted validations count (validations created by this publisher)
            submitted_reports_count = Validation.objects.filter(
                publisher=publisher
            ).count()
            
            # 3. Pending invoices count
            pending_invoices_count = Invoice.objects.filter(
                publisher=publisher,
                status__in=['Pending', 'Overdue']
            ).count()
            
        else:
            # User doesn't have a publisher object
            pending_validation_count = 0
            submitted_reports_count = 0
            pending_invoices_count = 0
            
    except Exception as e:
        print(f"Error calculating validation overview: {e}")
        pending_validation_count = 0
        submitted_reports_count = 0
        pending_invoices_count = 0
    
    # Generate chart data for last 7 days
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        try:
            # Determine which date field to use
            if hasattr(DailyRevenueSheet, 'date'):
                day_filter = {'date': day}
            elif hasattr(DailyRevenueSheet, 'start_date'):
                day_filter = {'start_date': day}
            elif hasattr(DailyRevenueSheet, 'created_at'):
                day_filter = {'created_at__date': day}
            else:
                day_revenue = day_profit = 0
                
            if 'day_filter' in locals():
                # Filter by publisher if user has one
                if hasattr(user, 'publisher'):
                    day_filter['publisher'] = user.publisher
                
                day_revenue = DailyRevenueSheet.objects.filter(
                    **day_filter
                ).aggregate(total=Sum('campaign_revenue'))['total'] or 0
                
                day_profit = DailyRevenueSheet.objects.filter(
                    **day_filter
                ).aggregate(total=Sum('profit'))['total'] or 0
            else:
                day_revenue = day_profit = 0
                
        except Exception as e:
            print(f"Error calculating day {day} revenue: {e}")
            day_revenue = day_profit = 0
            
        daily_stats.append({
            'date': day.strftime('%Y-%m-%d'), 
            'revenue': float(day_revenue), 
            'profit': float(day_profit)
        })
    
    daily_stats.reverse()
    labels = [item['date'] for item in daily_stats]
    revenues = [item['revenue'] for item in daily_stats]
    profits = [item['profit'] for item in daily_stats]

    context = {
        'total_income': total_income,
        'total_invoices': total_invoices,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'chart_labels': json.dumps(labels),
        'chart_revenues': json.dumps(revenues),
        'chart_profits': json.dumps(profits),
        
        # Validation overview context
        'pending_validation_count': pending_validation_count,
        'submitted_reports_count': submitted_reports_count,
        'pending_invoices_count': pending_invoices_count,
    }

    return render(request, 'dashboard/publisher_dashboard.html', context)

def default_dashboard(request):
    return render(request, "dashboard/default_dashboard.html")

def debug_user(request):
    return render(request, 'debug_user.html')

# -- LOGIN SUCCESS REDIRECT
def login_success(request):
    user = request.user
    if user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    elif user.role in ['admin', 'subadmin', 'dashboard']:  # Added 'dashboard' role
        return redirect('dashboard:admin_dashboard')
    elif user.role == 'publisher':
        return redirect('dashboard:publisher_dashboard')
    else:
        return redirect('dashboard:default_dashboard')