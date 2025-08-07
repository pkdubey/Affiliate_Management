from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from django.db.models import Sum

from apps.advertisers.models import Advertiser
from apps.publishers.models import Publisher
from apps.offers.models import Offer
from apps.invoicing.models import Invoice
from apps.dashboard.models import DashboardSnapshot

class Command(BaseCommand):
    help = 'Generate and store daily dashboard snapshot'

    def handle(self, *args, **kwargs):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        total_advertisers = Advertiser.objects.count()
        total_publishers = Publisher.objects.count()
        total_offers = Offer.objects.count()
        total_invoices = Invoice.objects.count()

        today_revenue = Invoice.objects.filter(created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0
        week_revenue = Invoice.objects.filter(created_at__date__gte=start_of_week).aggregate(total=Sum('amount'))['total'] or 0
        month_revenue = Invoice.objects.filter(created_at__date__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0

        status_summary = {}
        for entry in Invoice.objects.values('status').annotate(amount=Sum('amount')):
            status_summary[entry['status']] = float(entry['amount'])

        daily_revenue_data = []
        for i in range(7):
            day = today - timedelta(days=i)
            day_revenue = Invoice.objects.filter(created_at__date=day).aggregate(total=Sum('amount'))['total'] or 0
            daily_revenue_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'revenue': float(day_revenue)
            })
        daily_revenue_data.reverse()

        DashboardSnapshot.objects.update_or_create(
            date=today,
            defaults={
                'total_advertisers': total_advertisers,
                'total_publishers': total_publishers,
                'total_offers': total_offers,
                'total_invoices': total_invoices,
                'revenue_today': today_revenue,
                'revenue_week': week_revenue,
                'revenue_month': month_revenue,
                'invoice_status_summary': status_summary,
                'daily_revenue_data': daily_revenue_data,
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Dashboard snapshot created for {today}"))
