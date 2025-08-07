from django.views.generic import TemplateView

from django.shortcuts import render
# This app can be used for shared offer logic if needed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Offer
from .forms import OfferForm
from django.utils import timezone
from apps.offers.models import Offer, MatchHistory
from apps.publishers.models import Wishlist
from django.utils.dateparse import parse_date
from django.http import HttpResponse
import csv

class OffersMatcherResultsView(TemplateView):
    template_name = 'offers/matcher_results.html'

    def get(self, request, *args, **kwargs):
        from apps.offers.models import Offer, MatchHistory
        from apps.publishers.models import Wishlist

        # Fetch query params for manual matcher
        match_type = request.GET.get('match_type')
        offer_name = request.GET.get('offer_name', '').strip().lower()
        geo = request.GET.get('geo', '').strip().lower()

        matches = []
        suggestions = []
        # Date filter params for match history
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        if match_type and offer_name and geo:
            # Manual matcher logic
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()

            for wishlist in wishlists:
                for offer in offers:
                    cmp_offer_name = (offer.campaign_name or '').strip().lower()
                    cmp_wishlist_campaign = (wishlist.desired_campaign or '').strip().lower()
                    cmp_offer_geo = (offer.geo or '').strip().lower()
                    cmp_wishlist_geo = (wishlist.geo or '').strip().lower()
                    cmp_offer_category = (offer.category or '').strip().lower()
                    cmp_wishlist_category = (wishlist.category or '').strip().lower()

                    if match_type == 'exact':
                        if (
                            cmp_offer_name == offer_name and
                            cmp_offer_geo == geo and
                            cmp_offer_category == cmp_wishlist_category and
                            cmp_wishlist_campaign == cmp_offer_name
                        ):
                            matches.append({'wishlist': wishlist, 'offer': offer})

                    elif match_type == 'geo':
                        if cmp_offer_geo == geo and cmp_wishlist_geo == geo:
                            matches.append({'wishlist': wishlist, 'offer': offer})

                    elif match_type == 'category':
                        if cmp_offer_category == cmp_wishlist_category:
                            matches.append({'wishlist': wishlist, 'offer': offer})

            # Suggestions and match history left empty or you may decide to populate differently
            suggestions = []
            match_history = []

        else:
            # Existing normal functionality (strict matches + suggestions + match history)

            # Strict matches (exact)
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()

            for wishlist in wishlists:
                for offer in offers:
                    if (
                        offer.campaign_name.strip().lower() == wishlist.desired_campaign.strip().lower() and
                        offer.geo.strip().lower() == wishlist.geo.strip().lower() and
                        offer.category.strip().lower() == (wishlist.category or '').strip().lower()
                    ):
                        matches.append({'wishlist': wishlist, 'offer': offer})
                        # Save match history if not saved
                        MatchHistory.objects.get_or_create(offer=offer, wishlist=wishlist)
                    # Suggestions based on geo or category similarity
                    elif (
                        offer.geo.strip().lower() == wishlist.geo.strip().lower() or
                        offer.category.strip().lower() == (wishlist.category or '').strip().lower()
                    ):
                        suggestions.append({'wishlist': wishlist, 'offer': offer})

            # Remove duplicates from suggestions
            matched_pairs = {(m['wishlist'].id, m['offer'].id) for m in matches}
            suggestions = [
                s for s in suggestions
                if (s['wishlist'].id, s['offer'].id) not in matched_pairs
            ]

            match_history_qs = MatchHistory.objects.select_related('offer', 'wishlist').order_by('-matched_at')

            # Apply date filtering
            if start_date_str:
                start_date = parse_date(start_date_str)
                if start_date:
                    match_history_qs = match_history_qs.filter(matched_at__date__gte=start_date)
            if end_date_str:
                end_date = parse_date(end_date_str)
                if end_date:
                    match_history_qs = match_history_qs.filter(matched_at__date__lte=end_date)

            # Limit to 100
            match_history = match_history_qs[:100]

        # Export CSV for matches if requested
        if request.GET.get('export') == '1':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="matches.csv"'
            writer = csv.writer(response)

            # CSV Header row
            writer.writerow([
                'Publisher',
                'Wishlist Campaign',
                'Wishlist Geo',
                'Wishlist Category',
                'Wishlist Payout',
                'Wishlist Model',
                'Offer Campaign',
                'Offer Advertiser',
                'Offer Payout',
                'Offer Model',
            ])

            for pair in matches:
                writer.writerow([
                    pair['wishlist'].publisher.company_name if pair['wishlist'].publisher else '',
                    pair['wishlist'].desired_campaign,
                    pair['wishlist'].geo,
                    pair['wishlist'].category,
                    pair['wishlist'].payout if pair['wishlist'].payout is not None else '',
                    pair['wishlist'].model if pair['wishlist'].model else '',
                    pair['offer'].campaign_name,
                    pair['offer'].advertiser.company_name if pair['offer'].advertiser else '',
                    pair['offer'].payout if pair['offer'].payout is not None else '',
                    pair['offer'].model if pair['offer'].model else '',
                ])

            return response

        context = self.get_context_data(
            matches=matches,
            suggestions=suggestions,
            match_history=match_history,
            start_date=start_date_str,
            end_date=end_date_str,
            match_type=match_type,
            offer_name=offer_name,
            geo=geo,
        )
        return self.render_to_response(context)
    
class OffersMatcherView(TemplateView):
    template_name = 'offers/offers_matcher.html'

    def get(self, request, *args, **kwargs):
        offers = Offer.objects.filter(is_active=True)
        wishlists = Wishlist.objects.all()

        matches, suggestions = [], []

        # Build strict matches
        for wishlist in wishlists:
            for offer in offers:
                if (
                    offer.campaign_name.strip().lower() == wishlist.desired_campaign.strip().lower()
                    and offer.geo.strip().lower() == wishlist.geo.strip().lower()
                    and offer.category.strip().lower() == (wishlist.category or "").strip().lower()
                ):
                    matches.append({'wishlist': wishlist, 'offer': offer})
                    # Save match history if not already saved
                    MatchHistory.objects.get_or_create(
                        offer=offer, wishlist=wishlist
                    )
                # Suggest based on geo/category similarity (but not all match)
                elif (
                    offer.geo.strip().lower() == wishlist.geo.strip().lower()
                    or offer.category.strip().lower() == (wishlist.category or "").strip().lower()
                ):
                    suggestions.append({'wishlist': wishlist, 'offer': offer})

        # Remove strict matches from suggestions to avoid duplication
        matched_pairs = {(m['wishlist'].id, m['offer'].id) for m in matches}
        suggestions = [
            s for s in suggestions
            if (s['wishlist'].id, s['offer'].id) not in matched_pairs
        ]

        # Date filter parameters
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        match_history_qs = MatchHistory.objects.select_related('offer', 'wishlist').order_by('-matched_at')

        # Apply date filtering if dates provided and valid
        if start_date_str:
            start_date = parse_date(start_date_str)
            if start_date:
                match_history_qs = match_history_qs.filter(matched_at__date__gte=start_date)
        if end_date_str:
            end_date = parse_date(end_date_str)
            if end_date:
                match_history_qs = match_history_qs.filter(matched_at__date__lte=end_date)

        # Limit query to last 100 for display
        match_history = match_history_qs[:100]

        # Export CSV if requested
        if 'export' in request.GET:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="match_history.csv"'
            writer = csv.writer(response)
            # CSV header
            writer.writerow(['Matched At', 'Offer Campaign', 'Advertiser', 'Wishlist Campaign', 'Publisher'])
            for h in match_history_qs:
                writer.writerow([
                    h.matched_at.strftime('%Y-%m-%d %H:%M:%S'),
                    h.offer.campaign_name,
                    h.offer.advertiser.company_name if h.offer.advertiser else '',
                    h.wishlist.desired_campaign,
                    h.wishlist.publisher.company_name if h.wishlist.publisher else '',
                ])
            return response

        context = self.get_context_data(
            matches=matches,
            suggestions=suggestions,
            match_history=match_history,
            start_date=start_date_str,
            end_date=end_date_str,
        )
        return self.render_to_response(context)

class OfferListView(ListView):
    model = Offer
    template_name = 'offers/offer_list.html'
    context_object_name = 'offers'

class OfferCreateView(CreateView):
    model = Offer
    form_class = OfferForm
    template_name = 'offers/offer_form.html'
    success_url = reverse_lazy('offers:list')

class OfferUpdateView(UpdateView):
    model = Offer
    form_class = OfferForm
    template_name = 'offers/offer_form.html'
    success_url = reverse_lazy('offers:list')

class OfferDeleteView(DeleteView):
    model = Offer
    template_name = 'offers/offer_confirm_delete.html'
    success_url = reverse_lazy('offers:list')

class OfferDetailView(DetailView):
    model = Offer
    template_name = 'offers/offer_detail.html'
    context_object_name = 'offer'

# Create your views here.
