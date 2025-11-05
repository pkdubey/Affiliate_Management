from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Offer
from .forms import OfferForm
from django.utils import timezone
from apps.offers.models import Offer, MatchHistory
from apps.publishers.models import Wishlist
from django.utils.dateparse import parse_date
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import csv
import logging

logger = logging.getLogger(__name__)

class OffersMatcherResultsView(TemplateView):
    def write_matches_csv(self, matches):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="matches.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Publisher',
            'Wishlist Campaign',
            'Wishlist Geo',
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
            return (s or '').strip().upper()

        offer_name_norm = norm(offer_name_q)
        geo_norm = norm_geo(geo_q)

        matches, suggestions = [], []
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        # Decide if we have enough input to run manual matcher
        run_manual = False
        if match_type == 'exact':
            run_manual = bool(offer_name_norm and geo_norm)
        elif match_type == 'geo':
            run_manual = bool(geo_norm)

        if match_type and run_manual:
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()

            def offer_geo_set(offer) -> set:
                raw = getattr(offer, 'geo', '') or ''
                return {p.strip().upper() for p in raw.split(',') if p.strip()}

            def wl_geo_set(wl) -> set:
                raw = getattr(wl, 'geo', '') or ''
                return {p.strip().upper() for p in raw.split(',') if p.strip()}

            for wl in wishlists:
                cmp_wl_name = norm(getattr(wl, 'desired_campaign', ''))
                cmp_wl_geo_set = wl_geo_set(wl)

                for off in offers:
                    cmp_off_name = norm(getattr(off, 'campaign_name', ''))
                    cmp_off_geo_set = offer_geo_set(off)

                    if match_type == 'exact':
                        ok = (
                            cmp_off_name == offer_name_norm
                            and (geo_norm in cmp_off_geo_set)
                            and (geo_norm in cmp_wl_geo_set)
                            and cmp_wl_name == cmp_off_name
                        )
                        if ok:
                            matches.append({'wishlist': wl, 'offer': off})

                    elif match_type == 'geo':
                        if geo_norm and (geo_norm in cmp_off_geo_set) and (geo_norm in cmp_wl_geo_set):
                            matches.append({'wishlist': wl, 'offer': off})

            suggestions = []
            match_history = []

        else:
            # Default flow
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()
            for wl in wishlists:
                for off in offers:
                    if (
                        (off.campaign_name or '').strip().casefold()
                        == (wl.desired_campaign or '').strip().casefold()
                        and (off.geo or '').strip().casefold()
                        == (wl.geo or '').strip().casefold()
                    ):
                        matches.append({'wishlist': wl, 'offer': off})
                        MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                    elif (
                        (off.geo or '').strip().casefold()
                        == (wl.geo or '').strip().casefold()
                    ):
                        suggestions.append({'wishlist': wl, 'offer': off})

            matched_pairs = {(m['wishlist'].id, m['offer'].id) for m in matches}
            suggestions = [
                s for s in suggestions
                if (s['wishlist'].id, s['offer'].id) not in matched_pairs
            ]

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
    """
    Unified view for offers matching with partial search capability.
    - GET: Display empty matcher page with today's match history
    - POST: Handle AJAX search requests and return JSON with HTML results
    
    Search Features:
    - Case-insensitive partial matching for offer names
    - Support for multiple geo codes (comma-separated)
    - Automatic normalization of search terms
    """
    template_name = 'offers/offers_matcher.html'

    def write_match_history_csv(self, match_history_qs):
        """Generate CSV export for match history"""
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

    def _build_match_results_html(self, matches):
        """Build HTML for match results with simplified columns"""
        html_parts = []

        if matches:
            html_parts.append(
                '<h5 class="fw-bold mb-3 text-success"><i class="bi bi-check-circle"></i> Matches Found</h5>'
            )
            html_parts.append(
                '<div class="table-responsive mb-3"><table class="table table-striped table-bordered align-middle">'
            )
            html_parts.append(
                '<thead class="table-light"><tr>'
                '<th>Publisher</th><th>Offer</th><th>Advertiser</th><th>Geo</th>'
                '</tr></thead><tbody>'
            )

            for pair in matches:
                try:
                    publisher_name = pair['wishlist'].publisher.company_name if pair['wishlist'].publisher else '-'
                    offer_name = pair['offer'].campaign_name or '-'
                    advertiser_name = pair['offer'].advertiser.company_name if pair['offer'].advertiser else '-'
                    geo = pair['wishlist'].geo or '-'

                    html_parts.append(
                        f'<tr>'
                        f'<td><strong>{publisher_name}</strong></td>'
                        f'<td>{offer_name}</td>'
                        f'<td>{advertiser_name}</td>'
                        f'<td><span class="badge bg-info">{geo}</span></td>'
                        f'</tr>'
                    )
                except Exception as e:
                    logger.error(f"Error building match row: {e}")
                    continue

            html_parts.append('</tbody></table></div>')
            html_parts.append(f'<div class="alert alert-success"><strong>{len(matches)} match(es) found</strong></div>')

        else:
            html_parts.append(
                '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No matches found for your search criteria.</div>'
            )

        return ''.join(html_parts)

    def _perform_manual_match(self, match_type, offer_name_q, geo_q):
        """
        Perform manual matching based on search criteria.
        Supports:
        - PARTIAL matching for offer names (case-insensitive)
        - Case-insensitive geo matching
        - Both offer name and geo can be searched independently or together
        """
        def norm(s: str) -> str:
            """Normalize string: lowercase, strip whitespace"""
            return (s or '').strip().lower()

        def norm_geo(s: str) -> str:
            """Normalize geo: uppercase, strip whitespace"""
            return (s or '').strip().upper()

        offer_name_norm = norm(offer_name_q)
        geo_norm = norm_geo(geo_q)

        matches = []
        seen_pairs = set()  # Prevent duplicate matches

        try:
            offers = Offer.objects.filter(is_active=True)
            wishlists = Wishlist.objects.all()

            def offer_geo_set(offer) -> set:
                """Extract and normalize geo codes from offer"""
                raw = getattr(offer, 'geo', '') or ''
                return {p.strip().upper() for p in raw.split(',') if p.strip()}

            def wl_geo_set(wl) -> set:
                """Extract and normalize geo codes from wishlist"""
                raw = getattr(wl, 'geo', '') or ''
                return {p.strip().upper() for p in raw.split(',') if p.strip()}

            # Iterate through all wishlist-offer combinations
            for wl in wishlists:
                cmp_wl_name = norm(getattr(wl, 'desired_campaign', ''))
                cmp_wl_geo_set = wl_geo_set(wl)

                for off in offers:
                    cmp_off_name = norm(getattr(off, 'campaign_name', ''))
                    cmp_off_geo_set = offer_geo_set(off)

                    # Create a unique pair identifier
                    pair_id = (off.id, wl.id)
                    if pair_id in seen_pairs:
                        continue

                    if match_type == 'exact':
                        # Both offer name and geo must match
                        # Offer name: partial match (contains)
                        # Geo: must exist in both offer and wishlist
                        if (offer_name_norm and 
                            offer_name_norm in cmp_off_name and 
                            geo_norm and
                            geo_norm in cmp_off_geo_set and 
                            geo_norm in cmp_wl_geo_set):
                            
                            matches.append({'wishlist': wl, 'offer': off})
                            seen_pairs.add(pair_id)
                            MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                            logger.info(f"Exact match found: {off.campaign_name} (geo: {geo_norm}) <-> {wl.desired_campaign}")

                    elif match_type == 'geo':
                        # Match only on geo
                        # Both offer and wishlist must have the searched geo
                        if (geo_norm and
                            geo_norm in cmp_off_geo_set and 
                            geo_norm in cmp_wl_geo_set):
                            
                            matches.append({'wishlist': wl, 'offer': off})
                            seen_pairs.add(pair_id)
                            MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                            logger.info(f"Geo match found: {off.campaign_name} (geo: {geo_norm}) <-> {wl.desired_campaign}")

                    elif match_type == 'kpi':
                        # PARTIAL/SUBSTRING MATCH on offer name (case-insensitive)
                        # This allows searching "Uber" and finding "Uber India", "uber USA", "UBER Canada", etc.
                        if offer_name_norm and offer_name_norm in cmp_off_name:
                            
                            matches.append({'wishlist': wl, 'offer': off})
                            seen_pairs.add(pair_id)
                            MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                            logger.info(f"Partial match found: '{offer_name_q}' IN {off.campaign_name}")

        except Exception as e:
            logger.error(f"Error during manual match: {e}", exc_info=True)
            raise

        logger.info(f"Manual match completed: {len(matches)} matches found (Type: {match_type})")
        return matches

    def get(self, request, *args, **kwargs):
        """Handle GET requests - Display empty matcher page with today's match history"""
        today = timezone.now().date()
        today_match_history = MatchHistory.objects.select_related(
            'offer', 'wishlist', 'wishlist__publisher', 'offer__advertiser'
        ).filter(
            matched_at__date=today
        ).order_by('-matched_at')[:50]

        context = self.get_context_data(
            matches=[],
            match_history=today_match_history,
            start_date='',
            end_date='',
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Handle AJAX POST requests - Return JSON with match results"""
        try:
            match_type = (request.POST.get('match_type') or '').strip().lower()
            offer_name_q = (request.POST.get('offer_name') or '').strip()
            geo_q = (request.POST.get('geo') or '').strip()

            logger.info(f"Search Request - Type: {match_type}, Offer: '{offer_name_q}', Geo: '{geo_q}'")

            # Validate that at least one field is filled
            if not offer_name_q and not geo_q:
                return JsonResponse({
                    'html': '<div class="alert alert-warning"><strong>Please enter:</strong> Offer name or Geo to search</div>',
                    'status': 'error',
                }, status=400)

            # Perform matching
            matches = self._perform_manual_match(match_type, offer_name_q, geo_q)

            logger.info(f"Search Result - Found {len(matches)} matches")

            # Build HTML response
            html = self._build_match_results_html(matches)

            return JsonResponse({'html': html, 'status': 'success'})

        except Exception as e:
            logger.exception(f"Error in POST request: {e}")
            error_msg = f"Server error: {str(e)}"
            return JsonResponse({
                'html': f'<div class="alert alert-danger"><strong>Error:</strong> {error_msg}</div>',
                'status': 'error',
                'error': str(e)
            }, status=500)            
class OfferListView(ListView):
    """List all offers"""
    model = Offer
    template_name = 'offers/offer_list.html'
    context_object_name = 'offers'


class OfferCreateView(CreateView):
    """Create a new offer"""
    model = Offer
    form_class = OfferForm
    template_name = 'offers/offer_form.html'
    success_url = reverse_lazy('offers:list')


class OfferUpdateView(UpdateView):
    """Update an existing offer"""
    model = Offer
    form_class = OfferForm
    template_name = 'offers/offer_form.html'
    success_url = reverse_lazy('offers:list')


class OfferDeleteView(DeleteView):
    """Delete an offer"""
    model = Offer
    template_name = 'offers/offer_confirm_delete.html'
    success_url = reverse_lazy('offers:list')


class OfferDetailView(DetailView):
    """Display offer details"""
    model = Offer
    template_name = 'offers/offer_detail.html'
    context_object_name = 'offer'