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
    def write_matches_csv(self, matches):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="matches.csv"'
        writer = csv.writer(response)
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
                pair['wishlist'].payout or '',
                pair['wishlist'].model or '',
                pair['offer'].campaign_name,
                pair['offer'].advertiser.company_name if pair['offer'].advertiser else '',
                pair['offer'].payout or '',
                pair['offer'].model or '',
            ])
        return response
    template_name = 'offers/matcher_results.html'

    def get(self, request, *args, **kwargs):
        from apps.offers.models import Offer, MatchHistory
        from apps.publishers.models import Wishlist

        match_type = (request.GET.get('match_type') or '').strip().lower()
        offer_name_q = (request.GET.get('offer_name') or '').strip()
        geo_q = (request.GET.get('geo') or '').strip()

        # Normalized helpers
        def norm(s: str) -> str:
            return (s or '').strip().casefold()

        def norm_geo(s: str) -> str:
            # For country codes, uppercase is common; casefold also fine. Use upper for readability.
            return (s or '').strip().upper()

        offer_name_norm = norm(offer_name_q)
        geo_norm = norm_geo(geo_q)

        matches, suggestions = [], []
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        # Decide if we have enough input to run manual matcher
        run_manual = False
        if match_type == 'exact':
            # Expect both name and geo
            run_manual = bool(offer_name_norm and geo_norm)
        elif match_type == 'geo':
            # Allow geo-only OR both
            run_manual = bool(geo_norm)
        elif match_type == 'category':
            # Category uses DB fields, no need for offer_name/geo
            run_manual = True

        if match_type and run_manual:
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()

            # Helper to normalize stored values
            def offer_geo_set(offer) -> set:
                # Support "IN,US, UK" -> {"IN","US","UK"}
                raw = getattr(offer, 'geo', '') or ''
                parts = [p.strip().upper() for p in raw.split(',') if p.strip()]
                return set(parts) if parts else set()

            def wl_geo_set(wl) -> set:
                raw = getattr(wl, 'geo', '') or ''
                parts = [p.strip().upper() for p in raw.split(',') if p.strip()]
                return set(parts) if parts else set()

            for wl in wishlists:
                cmp_wl_name = norm(getattr(wl, 'desired_campaign', ''))
                cmp_wl_geo_set = wl_geo_set(wl)
                cmp_wl_cat = norm(getattr(wl, 'category', ''))

                for off in offers:
                    cmp_off_name = norm(getattr(off, 'campaign_name', ''))
                    cmp_off_geo_set = offer_geo_set(off)
                    cmp_off_cat = norm(getattr(off, 'category', ''))

                    if match_type == 'exact':
                        # exact: name and single-geo exact match, plus wishlist name equals offer name and category equal
                        ok = (
                            cmp_off_name == offer_name_norm and
                            (geo_norm in cmp_off_geo_set) and
                            (geo_norm in cmp_wl_geo_set) and
                            cmp_off_cat == cmp_wl_cat and
                            cmp_wl_name == cmp_off_name
                        )
                        if ok:
                            matches.append({'wishlist': wl, 'offer': off})

                    elif match_type == 'geo':
                        # geo: match if selected GEO is present in BOTH offer and wishlist
                        if geo_norm and (geo_norm in cmp_off_geo_set) and (geo_norm in cmp_wl_geo_set):
                            matches.append({'wishlist': wl, 'offer': off})

                    elif match_type == 'category':
                        if cmp_off_cat == cmp_wl_cat:
                            matches.append({'wishlist': wl, 'offer': off})

            suggestions = []
            match_history = []
        else:
            # Existing normal flow unchanged...
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()
            for wl in wishlists:
                for off in offers:
                    if (
                        (off.campaign_name or '').strip().casefold() == (wl.desired_campaign or '').strip().casefold() and
                        (off.geo or '').strip().casefold() == (wl.geo or '').strip().casefold() and
                        (off.category or '').strip().casefold() == ((wl.category or '')).strip().casefold()
                    ):
                        matches.append({'wishlist': wl, 'offer': off})
                        MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                    elif (
                        (off.geo or '').strip().casefold() == (wl.geo or '').strip().casefold() or
                        (off.category or '').strip().casefold() == ((wl.category or '')).strip().casefold()
                    ):
                        suggestions.append({'wishlist': wl, 'offer': off})

            matched_pairs = {(m['wishlist'].id, m['offer'].id) for m in matches}
            suggestions = [s for s in suggestions if (s['wishlist'].id, s['offer'].id) not in matched_pairs]

            match_history_qs = MatchHistory.objects.select_related('offer', 'wishlist').order_by('-matched_at')
            from django.utils.dateparse import parse_date
            if start_date_str:
                sd = parse_date(start_date_str)
                if sd:
                    match_history_qs = match_history_qs.filter(matched_at__date__gte=sd)
            if end_date_str:
                ed = parse_date(end_date_str)
                if ed:
                    match_history_qs = match_history_qs.filter(matched_at__date__lte=ed)
            match_history = match_history_qs[:100]

        if request.GET.get('export') == '1':
            return self.write_matches_csv(matches)

        context = self.get_context_data(
            matches=matches,
            suggestions=suggestions,
            match_history=match_history,
            start_date=start_date_str,
            end_date=end_date_str,
            match_type=match_type,
            offer_name=offer_name_q,
            geo=geo_q,
        )
        return self.render_to_response(context)

class OffersMatcherView(TemplateView):
    def write_match_history_csv(self, match_history_qs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="match_history.csv"'
        writer = csv.writer(response)
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
            return self.write_match_history_csv(match_history_qs)

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
