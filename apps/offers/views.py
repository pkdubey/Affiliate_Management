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
    Unified view for offers matching with exact match capability.
    - GET: Display empty matcher page with today's match history
    - POST: Handle AJAX search requests and return JSON with HTML results
    
    Search Features:
    - Case-insensitive EXACT matching for offer names
    - Case-insensitive EXACT matching for geo codes
    - Dynamic matching (works for all data, not static)
    - Behavior:
      * Offer name only → Match offer name exactly with ANY wishlist
      * Geo only → Match geo exactly across all publishers/offers
      * Both → Match offer name + geo exactly with matching wishlists
    - Prevents duplicate display of same match data
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
        """Build HTML for match results with simplified columns - NO DUPLICATES"""
        html_parts = []

        if matches:
            # Additional deduplication based on display values
            seen_display = set()
            unique_matches = []
            
            for pair in matches:
                try:
                    publisher_name = pair['wishlist'].publisher.company_name if pair['wishlist'].publisher else '-'
                    offer_name = pair['offer'].campaign_name or '-'
                    advertiser_name = pair['offer'].advertiser.company_name if pair['offer'].advertiser else '-'
                    geo = pair['wishlist'].geo or '-'
                    
                    # Create a unique key based on actual display values
                    display_key = (
                        publisher_name.strip().lower(),
                        offer_name.strip().lower(),
                        advertiser_name.strip().lower(),
                        geo.strip().lower()
                    )
                    
                    if display_key not in seen_display:
                        seen_display.add(display_key)
                        unique_matches.append({
                            'publisher': publisher_name,
                            'offer': offer_name,
                            'advertiser': advertiser_name,
                            'geo': geo,
                            'pair': pair
                        })
                except Exception as e:
                    logger.error(f"Error processing match row: {e}")
                    continue
            
            if unique_matches:
                html_parts.append(
                    '<h5 class="fw-bold mb-3 text-success"><i class="bi bi-check-circle"></i> Exact Matches Found</h5>'
                )
                html_parts.append(
                    '<div class="table-responsive mb-3"><table class="table table-striped table-bordered align-middle">'
                )
                html_parts.append(
                    '<thead class="table-light"><tr>'
                    '<th>Publisher</th><th>Offer</th><th>Advertiser</th><th>Geo</th>'
                    '</tr></thead><tbody>'
                )

                for match in unique_matches:
                    html_parts.append(
                        f'<tr>'
                        f'<td><strong>{match["publisher"]}</strong></td>'
                        f'<td>{match["offer"]}</td>'
                        f'<td>{match["advertiser"]}</td>'
                        f'<td><span class="badge bg-info">{match["geo"]}</span></td>'
                        f'</tr>'
                    )

                html_parts.append('</tbody></table></div>')
                html_parts.append(f'<div class="alert alert-success"><strong>{len(unique_matches)} exact match(es) found</strong></div>')
            else:
                html_parts.append(
                    '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No exact matches found.</div>'
                )
        else:
            html_parts.append(
                '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No matches found for your search criteria.</div>'
            )

        return ''.join(html_parts)

    def _perform_manual_match(self, offer_name_q, geo_q):
        """
        Perform manual matching based on search criteria.
        - EXACT matching only (case-insensitive)
        - Dynamic matching for all data (no static publisher filters)
        - No duplicate (offer, wishlist) pairs in response.
        
        Search Logic:
        1. If ONLY offer_name is provided:
        → Find ALL offers with exact matching name
        → Match with wishlists that:
            a) Have ANY matching geo with the offer
            b) Are from a publisher whose company name matches the offer's advertiser company name
        2. If ONLY geo is provided:
        → Find ALL wishlists with exact matching geo
        → Match with ALL offers that have exact matching geo
        3. If BOTH are provided:
        → Find offers with exact matching name AND exact geo
        → Match with wishlists that have exact matching geo AND matching offer name
        """
        def norm(s):
            return (s or '').strip().lower()
        
        def norm_geo(s):
            return (s or '').strip().upper()

        offer_name_norm = norm(offer_name_q)
        geo_norm = norm_geo(geo_q)

        matches = []
        seen_pairs = set()  # Prevent duplicate ID pairs

        logger.info(f"🔍 Starting search - Offer (norm): '{offer_name_norm}', Geo (norm): '{geo_norm}'")

        try:
            # Use select_related to optimize database queries
            offers = Offer.objects.filter(is_active=True).select_related('advertiser')
            wishlists = Wishlist.objects.all().select_related('publisher')
            
            logger.info(f"📊 Total offers: {offers.count()}, Total wishlists: {wishlists.count()}")
            
            def geo_set(val):
                """Given a geo string, return a set of uppercase geo codes."""
                return {g.strip().upper() for g in (val or '').split(',') if g.strip()}

            def has_geo_match(search_geo, target_geos):
                """Check if search geo exists in target geo set"""
                return search_geo in target_geos if target_geos else False

            # CASE 1: ONLY offer_name is provided (no geo)
            if offer_name_norm and not geo_norm:
                logger.info("🎯 Search Mode: OFFER NAME ONLY")
                
                # Find all offers with exact matching name
                matching_offers = []
                for off in offers:
                    off_name = norm(getattr(off, 'campaign_name', ''))
                    if off_name == offer_name_norm:
                        matching_offers.append(off)
                        logger.info(f"✅ Found matching offer: '{off_name}' from advertiser: '{off.advertiser.company_name if off.advertiser else 'N/A'}'")
                
                if not matching_offers:
                    logger.info("❌ No offers found with matching name")
                    return []
                
                # For each matching offer, match with wishlists that:
                # 1. Have ANY geo overlap with the offer
                # 2. Are from a publisher whose company name matches the offer's advertiser company name
                for off in matching_offers:
                    off_geos = geo_set(getattr(off, 'geo', ''))
                    offer_advertiser_name = off.advertiser.company_name if off.advertiser else None
                    
                    if not offer_advertiser_name:
                        logger.warning(f"⚠️ Offer '{off.campaign_name}' has no advertiser, skipping")
                        continue
                    
                    logger.info(f"🔍 Looking for wishlists from publisher matching advertiser: '{offer_advertiser_name}'")
                    
                    for wl in wishlists:
                        # Check if wishlist has a publisher
                        if not wl.publisher:
                            continue
                        
                        wl_geos = geo_set(getattr(wl, 'geo', ''))
                        publisher_name = wl.publisher.company_name
                        
                        # Check BOTH conditions:
                        # 1. Geo overlap
                        # 2. Publisher company name matches advertiser company name
                        geo_overlap = off_geos and wl_geos and off_geos.intersection(wl_geos)
                        company_match = publisher_name and offer_advertiser_name and publisher_name.strip().lower() == offer_advertiser_name.strip().lower()
                        
                        if geo_overlap and company_match:
                            pair_id = (off.id, wl.id)
                            if pair_id not in seen_pairs:
                                matches.append({'wishlist': wl, 'offer': off})
                                seen_pairs.add(pair_id)
                                MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                logger.info(f"  ✅ Matched with wishlist from publisher: '{publisher_name}' (Advertiser: '{offer_advertiser_name}')")
                        elif company_match and not geo_overlap:
                            logger.info(f"  ⚠️ Publisher '{publisher_name}' matches advertiser but no geo overlap")
                        elif geo_overlap and not company_match:
                            logger.info(f"  ⚠️ Geo overlap but publisher '{publisher_name}' doesn't match advertiser '{offer_advertiser_name}'")
                
                # If no matches found with the company name constraint, show a message
                if not matches:
                    logger.info("ℹ️ No matches found where publisher company matches advertiser company")
            
            # CASE 2: ONLY geo is provided (no offer_name)
            elif geo_norm and not offer_name_norm:
                logger.info(f"🌍 Search Mode: GEO ONLY (searching for: {geo_norm})")
                
                # Find all wishlists with matching geo
                matching_wishlists = []
                for wl in wishlists:
                    wl_geos = geo_set(getattr(wl, 'geo', ''))
                    if has_geo_match(geo_norm, wl_geos):
                        matching_wishlists.append(wl)
                        pub_name = wl.publisher.company_name if wl.publisher else 'N/A'
                        logger.info(f"✅ Found matching geo '{geo_norm}' in wishlist from publisher: {pub_name}")
                
                if not matching_wishlists:
                    logger.info("❌ No wishlists found with matching geo")
                    return []
                
                # Find all offers with matching geo
                matching_offers = []
                for off in offers:
                    off_geos = geo_set(getattr(off, 'geo', ''))
                    if has_geo_match(geo_norm, off_geos):
                        matching_offers.append(off)
                        logger.info(f"✅ Found matching geo '{geo_norm}' in offer: {off.campaign_name}")
                
                logger.info(f"📊 Found {len(matching_offers)} offers with geo '{geo_norm}'")
                
                # Create matches between ALL wishlists and offers that have the matching geo
                for wl in matching_wishlists:
                    for off in matching_offers:
                        pair_id = (off.id, wl.id)
                        if pair_id not in seen_pairs:
                            matches.append({'wishlist': wl, 'offer': off})
                            seen_pairs.add(pair_id)
                            MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                            logger.info(f"  ➜ Matched offer '{off.campaign_name}' with wishlist from publisher '{wl.publisher.company_name if wl.publisher else 'N/A'}'")
            
            # CASE 3: BOTH offer_name and geo are provided
            elif offer_name_norm and geo_norm:
                logger.info(f"🎯 Search Mode: BOTH OFFER NAME AND GEO (offer: '{offer_name_norm}', geo: '{geo_norm}')")
                
                # Find offers with exact name AND geo match
                matching_offers = []
                for off in offers:
                    off_name = norm(getattr(off, 'campaign_name', ''))
                    off_geos = geo_set(getattr(off, 'geo', ''))
                    
                    if off_name == offer_name_norm and has_geo_match(geo_norm, off_geos):
                        matching_offers.append(off)
                        logger.info(f"✅ Found matching offer: '{off_name}' with geo '{geo_norm}' from advertiser: '{off.advertiser.company_name if off.advertiser else 'N/A'}'")
                
                if not matching_offers:
                    logger.info("❌ No offers found with matching name and geo")
                    return []
                
                # Find wishlists with matching geo AND matching offer name
                matching_wishlists = []
                for wl in wishlists:
                    wl_name = norm(getattr(wl, 'desired_campaign', ''))
                    wl_geos = geo_set(getattr(wl, 'geo', ''))
                    
                    # Check if wishlist has the matching geo AND offer name
                    if has_geo_match(geo_norm, wl_geos) and wl_name == offer_name_norm:
                        matching_wishlists.append(wl)
                        pub_name = wl.publisher.company_name if wl.publisher else 'N/A'
                        logger.info(f"✅ Found matching wishlist: '{wl_name}' with geo '{geo_norm}' from publisher: {pub_name}")
                
                logger.info(f"📊 Found {len(matching_wishlists)} wishlists with both name and geo match")
                
                # Create matches between matching offers and matching wishlists
                # Also check if publisher company matches advertiser company
                for off in matching_offers:
                    offer_advertiser_name = off.advertiser.company_name if off.advertiser else None
                    
                    for wl in matching_wishlists:
                        if not wl.publisher:
                            continue
                        
                        publisher_name = wl.publisher.company_name
                        company_match = publisher_name and offer_advertiser_name and publisher_name.strip().lower() == offer_advertiser_name.strip().lower()
                        
                        if company_match:
                            pair_id = (off.id, wl.id)
                            if pair_id not in seen_pairs:
                                matches.append({'wishlist': wl, 'offer': off})
                                seen_pairs.add(pair_id)
                                MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                logger.info(f"  ✅ Matched with wishlist from publisher: '{publisher_name}' (Advertiser: '{offer_advertiser_name}')")
                        
        except Exception as e:
            logger.error(f"❌ Error during manual match: {e}", exc_info=True)
            raise

        logger.info(f"✅ Manual match completed: {len(matches)} exact matches found")
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
            offer_name_q = (request.POST.get('offer_name') or '').strip()
            geo_q = (request.POST.get('geo') or '').strip()

            logger.info(f"📨 Search Request - Offer: '{offer_name_q}', Geo: '{geo_q}'")

            # Validate that at least one field is filled
            if not offer_name_q and not geo_q:
                return JsonResponse({
                    'html': '<div class="alert alert-warning"><strong>Please enter:</strong> Offer name or Geo to search</div>',
                    'status': 'error',
                }, status=400)

            # Perform matching
            matches = self._perform_manual_match(offer_name_q, geo_q)

            logger.info(f"📊 Search Result - Found {len(matches)} exact matches")

            # Build HTML response
            html = self._build_match_results_html(matches)

            return JsonResponse({'html': html, 'status': 'success'})

        except Exception as e:
            logger.exception(f"❌ Error in POST request: {e}")
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