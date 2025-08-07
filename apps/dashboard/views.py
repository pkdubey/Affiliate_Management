from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from apps.advertisers.models import Advertiser
from apps.publishers.models import Publisher
from apps.offers.models import Offer
from apps.invoicing.models import Invoice
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from decimal import Decimal
import json

@login_required
@role_required(allowed_roles=['admin', 'subadmin'])
def dashboard_view(request):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Metrics
    total_advertisers = Advertiser.objects.count()
    total_publishers = Publisher.objects.count()
    total_offers = Offer.objects.count()
    total_invoices = Invoice.objects.count()

    # Invoices by status (note: count here is actually a summed revenue, not a count!)
    invoice_status_counts = Invoice.objects.values('status').annotate(count=Sum('drs__campaign_revenue'))

    # Revenue
    today_revenue = Invoice.objects.filter(created_at__date=today).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0
    week_revenue = Invoice.objects.filter(created_at__date__gte=start_of_week).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0
    month_revenue = Invoice.objects.filter(created_at__date__gte=start_of_month).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0

    # Ensure these are simple numbers, not Decimal
    today_revenue = float(today_revenue) if today_revenue is not None else 0.0
    week_revenue = float(week_revenue) if week_revenue is not None else 0.0
    month_revenue = float(month_revenue) if month_revenue is not None else 0.0

    # Graph data for last 7 days
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_revenue = Invoice.objects.filter(created_at__date=day).aggregate(total=Sum('drs__campaign_revenue'))['total'] or 0
        day_revenue = float(day_revenue) if day_revenue is not None else 0.0

        # Calculate profit for the day (replace with your actual profit logic)
        day_profit = Invoice.objects.filter(created_at__date=day).aggregate(total=Sum('drs__profit'))['total'] or 0
        day_profit = float(day_profit) if day_profit is not None else 0.0

        daily_stats.append({'date': day.strftime('%Y-%m-%d'), 'revenue': day_revenue, 'profit': day_profit})
    daily_stats.reverse()

    labels = [item['date'] for item in daily_stats]
    revenues = [item['revenue'] for item in daily_stats]   # Already float
    profits = [item['profit'] for item in daily_stats]     # Already float

    # If you ever build chart data lists from DB directly without this loop, do conversion to float too

    context = {
        'total_advertisers': total_advertisers,
        'total_publishers': total_publishers,
        'total_offers': total_offers,
        'total_invoices': total_invoices,
        'invoice_status_counts': invoice_status_counts,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'chart_labels': json.dumps(labels),
        'chart_revenues': json.dumps(revenues),
        'chart_profits': json.dumps(profits),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@role_required(allowed_roles=['publisher'])
def publisher_dashboard(request):
    # Minimal logic for now; expand with publisher-specific stats later
    return render(request, 'dashboard/publisher_dashboard.html')


def login_success(request):
    user = request.user
    if user.is_superuser:
        return redirect('super_admin_dashboard')
    elif hasattr(user, 'is_admin') and user.is_admin:
        return redirect('admin_dashboard')
    elif hasattr(user, 'is_publisher') and user.is_publisher:
        return redirect('publisher_dashboard')
    else:
        return redirect('default_dashboard')