from django.core.management.base import BaseCommand
from apps.invoicing.models import CurrencyRate

class Command(BaseCommand):
    help = 'Manually update currency rates to INR (no API, no internet)'

    def handle(self, *args, **kwargs):
        # UPDATE these values whenever you need new rates
        rates = {
            'USD': 0.0120,  # 1 INR = 0.012 USD (July 2025 example; use up-to-date rates)
            'EUR': 0.0110,  # 1 INR = 0.011 EUR
            # Add more currencies if needed
        }
        for currency, rate in rates.items():
            CurrencyRate.objects.update_or_create(
                currency=currency,
                defaults={'rate_to_inr': rate},
            )
            self.stdout.write(self.style.SUCCESS(f"Set 1 INR = {rate} {currency}"))
        self.stdout.write(self.style.SUCCESS("Currency rates UPDATED (manual/hardcoded)"))
