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
from datetime import datetime

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
    - Case-insensitive partial matching for offer names
    - Case-insensitive EXACT matching for geo codes
    - Dynamic matching (works for all data, not static)
    - Behavior:
      * Offer name only → Match offer name partially with ANY wishlist
      * Geo only → Match geo exactly across all publishers/offers
      * Both → Match offer name partially + geo exactly with matching wishlists
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
                    '<h5 class="fw-bold mb-3 text-success"><i class="bi bi-check-circle"></i> Matches Found</h5>'
                )
                html_parts.append(
                    '<div class="table-responsive mb-3"><table class="table table-striped table-bordered align-middle">'
                )
                html_parts.append(
                    '<thead class="table-light"><tr>'
                    '<th>Publisher</th><th>Offer</th><th>Advertiser</th><th>Geo</th><th>Match Type</th>'
                    '</tr></thead><tbody>'
                )

                for match in unique_matches:
                    match_type = match['pair'].get('match_type', 'match').replace('_', ' ').title()
                    html_parts.append(
                        f'<tr>'
                        f'<td><strong>{match["publisher"]}</strong></td>'
                        f'<td>{match["offer"]}</td>'
                        f'<td>{match["advertiser"]}</td>'
                        f'<td><span class="badge bg-info">{match["geo"]}</span></td>'
                        f'<td><span class="badge bg-success">{match_type}</span></td>'
                        f'</tr>'
                    )

                html_parts.append('</tbody></table></div>')
                html_parts.append(f'<div class="alert alert-success"><strong>{len(unique_matches)} match(es) found</strong></div>')
            else:
                html_parts.append(
                    '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No matches found.</div>'
                )
        else:
            html_parts.append(
                '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No matches found for your search criteria.</div>'
            )

        return ''.join(html_parts)

    def _perform_manual_match(self, offer_name_q, geo_q):
        """Match based on: 1) Company name matching OR 2) Offer name partial matching"""
        def norm(s):
            return (s or '').strip().lower()
        
        def norm_geo(s):
            return (s or '').strip().upper()
        
        def contains_partial(search_term, target_string):
            """Check if search term is contained in target string (case-insensitive)"""
            if not search_term:
                return True
            if not target_string:
                return False
            return search_term in norm(target_string)

        offer_name_norm = norm(offer_name_q)
        geo_norm = norm_geo(geo_q)

        matches = []
        seen_pairs = set()

        logger.info(f"🔍 Starting search - Offer: '{offer_name_norm}', Geo: '{geo_norm}'")

        try:
            offers = Offer.objects.filter(is_active=True).select_related('advertiser')
            wishlists = Wishlist.objects.all().select_related('publisher')
            
            def geo_set(val):
                """Return set of geo codes, empty if val is None/empty"""
                if not val:
                    return set()
                return {g.strip().upper() for g in val.split(',') if g.strip()}

            def has_geo_match(search_geo, target_geos):
                """Check if search geo exists in target geo set."""
                if not search_geo:  # If no geo specified in search, match everything
                    return True
                if not target_geos:  # If target has no geo, still consider it a match
                    return True
                return search_geo in target_geos
            
            def get_field_value(obj, field_name, default=''):
                """Safely get field value, return default if None/empty"""
                value = getattr(obj, field_name, default)
                return value if value is not None else default
            
            def field_match(offer_field, wishlist_field, field_name, exact_match=True):
                """Check if fields match. If either is empty, consider it a match."""
                if not offer_field and not wishlist_field:
                    # Both empty - consider it a match
                    return True
                elif not offer_field or not wishlist_field:
                    # One is empty, one has value - still consider it a match
                    return True
                elif exact_match:
                    return norm(offer_field) == norm(wishlist_field)
                else:
                    # For numeric fields like payout, allow range matching
                    try:
                        return float(offer_field) >= float(wishlist_field)  # Offer payout >= desired payout
                    except (ValueError, TypeError):
                        return norm(offer_field) == norm(wishlist_field)
            
            # Get all advertiser and publisher company names
            advertiser_companies = {}
            publisher_companies = {}
            
            # Build advertiser company dictionary
            for off in offers:
                if off.advertiser and off.advertiser.company_name:
                    company_norm = norm(off.advertiser.company_name)
                    advertiser_companies[company_norm] = advertiser_companies.get(company_norm, []) + [off]
                else:
                    advertiser_companies['_no_company'] = advertiser_companies.get('_no_company', []) + [off]
            
            # Build publisher company dictionary
            for wl in wishlists:
                if wl.publisher and wl.publisher.company_name:
                    company_norm = norm(wl.publisher.company_name)
                    publisher_companies[company_norm] = publisher_companies.get(company_norm, []) + [wl]
                else:
                    publisher_companies['_no_company'] = publisher_companies.get('_no_company', []) + [wl]
            
            # Find companies that exist in BOTH advertisers and publishers
            all_companies = set(advertiser_companies.keys()).union(set(publisher_companies.keys()))
            common_companies = set(advertiser_companies.keys()).intersection(set(publisher_companies.keys()))
            
            logger.info(f"🏢 Found {len(common_companies)} common companies and {len(all_companies)} total companies")
            
            # CASE 1: ONLY offer_name is provided (partial match)
            if offer_name_norm and not geo_norm:
                logger.info("🎯 Search Mode: OFFER NAME ONLY (partial matching)")
                
                # Find ALL offers with PARTIAL name match
                matching_offers_by_name = []
                for off in offers:
                    off_name = norm(get_field_value(off, 'campaign_name'))
                    if contains_partial(offer_name_norm, off_name):
                        matching_offers_by_name.append(off)
                
                logger.info(f"📊 Found {len(matching_offers_by_name)} offers with name containing '{offer_name_norm}'")
                
                # Try TWO matching strategies:
                # 1. Match by COMPANY NAME (between advertiser and publisher)
                # 2. Match by OFFER NAME (partial match between offer campaign_name and wishlist desired_campaign)
                
                # STRATEGY 1: Match by COMPANY NAME
                if matching_offers_by_name:
                    logger.info("🔍 Strategy 1: Matching by COMPANY NAME")
                    for off in matching_offers_by_name:
                        off_geos = geo_set(get_field_value(off, 'geo'))
                        off_company = norm(off.advertiser.company_name) if off.advertiser and off.advertiser.company_name else '_no_company'
                        
                        # Get matching publisher companies
                        companies_to_match = [off_company] if off_company != '_no_company' else list(publisher_companies.keys())
                        
                        for company in companies_to_match:
                            for wl in publisher_companies.get(company, []):
                                wl_geos = geo_set(get_field_value(wl, 'geo'))
                                
                                # Check geo overlap (allow empty geos)
                                geo_overlap = not off_geos or not wl_geos or off_geos.intersection(wl_geos)
                                
                                # Check other fields (allow empty/null)
                                payout_match = field_match(
                                    get_field_value(off, 'payout'),
                                    get_field_value(wl, 'desired_payout'),
                                    'payout',
                                    exact_match=False
                                )
                                
                                kpi_match = field_match(
                                    get_field_value(off, 'kpi'),
                                    get_field_value(wl, 'desired_kpi'),
                                    'kpi'
                                )
                                
                                model_match = field_match(
                                    get_field_value(off, 'model'),
                                    get_field_value(wl, 'desired_model'),
                                    'model'
                                )
                                
                                if geo_overlap and payout_match and kpi_match and model_match:
                                    pair_id = (off.id, wl.id)
                                    if pair_id not in seen_pairs:
                                        matches.append({
                                            'wishlist': wl, 
                                            'offer': off,
                                            'match_reason': f"Company match: {company if company != '_no_company' else 'No company specified'}",
                                            'match_type': 'company'
                                        })
                                        seen_pairs.add(pair_id)
                                        MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                        logger.info(f"✅ Company Match: Offer '{off.campaign_name}' with wishlist from publisher '{company}'")
                
                # STRATEGY 2: Match by OFFER NAME (partial match)
                logger.info("🔍 Strategy 2: Matching by OFFER NAME (partial matching)")
                
                # Find all wishlists that have PARTIAL matching offer name
                matching_wishlists_by_name = []
                for wl in wishlists:
                    wl_name = norm(get_field_value(wl, 'desired_campaign'))
                    if contains_partial(offer_name_norm, wl_name):
                        matching_wishlists_by_name.append(wl)
                
                logger.info(f"📊 Found {len(matching_wishlists_by_name)} wishlists looking for offers containing '{offer_name_norm}'")
                
                # Match offers with wishlists that have similar desired campaign name
                for off in offers:
                    off_name = norm(get_field_value(off, 'campaign_name'))
                    if contains_partial(offer_name_norm, off_name):
                        off_geos = geo_set(get_field_value(off, 'geo'))
                        
                        for wl in matching_wishlists_by_name:
                            wl_name = norm(get_field_value(wl, 'desired_campaign'))
                            wl_geos = geo_set(get_field_value(wl, 'geo'))
                            
                            # Check if both contain the search term (partial match)
                            both_contain_search = (contains_partial(offer_name_norm, off_name) and 
                                                 contains_partial(offer_name_norm, wl_name))
                            
                            # Check geo overlap
                            geo_overlap = not off_geos or not wl_geos or off_geos.intersection(wl_geos)
                            
                            # Check other fields
                            payout_match = field_match(
                                get_field_value(off, 'payout'),
                                get_field_value(wl, 'desired_payout'),
                                'payout',
                                exact_match=False
                            )
                            
                            kpi_match = field_match(
                                get_field_value(off, 'kpi'),
                                get_field_value(wl, 'desired_kpi'),
                                'kpi'
                            )
                            
                            model_match = field_match(
                                get_field_value(off, 'model'),
                                get_field_value(wl, 'desired_model'),
                                'model'
                            )
                            
                            if both_contain_search and geo_overlap and payout_match and kpi_match and model_match:
                                pair_id = (off.id, wl.id)
                                if pair_id not in seen_pairs:
                                    # Check if companies also match
                                    off_company = norm(off.advertiser.company_name) if off.advertiser and off.advertiser.company_name else ''
                                    wl_company = norm(wl.publisher.company_name) if wl.publisher and wl.publisher.company_name else ''
                                    
                                    if off_company == wl_company and off_company:
                                        match_type = 'company_and_name'
                                        match_reason = f"Both company and offer name match: {off_company}"
                                    else:
                                        match_type = 'offer_name'
                                        match_reason = f"Offer name partial match: '{offer_name_norm}'"
                                    
                                    matches.append({
                                        'wishlist': wl, 
                                        'offer': off,
                                        'match_reason': match_reason,
                                        'match_type': match_type
                                    })
                                    seen_pairs.add(pair_id)
                                    MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                    logger.info(f"✅ {match_type.upper()} Match: Offer '{off.campaign_name}' with wishlist")
            
            # CASE 2: ONLY geo is provided
            elif geo_norm and not offer_name_norm:
                logger.info(f"🌍 Search Mode: GEO ONLY (searching for: {geo_norm})")
                
                # Match based on geo with TWO strategies:
                # 1. Same company + same geo
                # 2. Any geo match
                
                # STRATEGY 1: Same company + same geo
                logger.info("🔍 Strategy 1: Matching by COMPANY + GEO")
                for company in common_companies:
                    # Get offers and wishlists from same company
                    for off in advertiser_companies.get(company, []):
                        off_geos = geo_set(get_field_value(off, 'geo'))
                        if has_geo_match(geo_norm, off_geos):
                            for wl in publisher_companies.get(company, []):
                                wl_geos = geo_set(get_field_value(wl, 'geo'))
                                if has_geo_match(geo_norm, wl_geos):
                                    pair_id = (off.id, wl.id)
                                    if pair_id not in seen_pairs:
                                        matches.append({
                                            'wishlist': wl, 
                                            'offer': off,
                                            'match_reason': f"Company and geo match: {company}",
                                            'match_type': 'company_and_geo'
                                        })
                                        seen_pairs.add(pair_id)
                                        MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                        logger.info(f"✅ Company+Geo Match: {company} with geo '{geo_norm}'")
                
                # STRATEGY 2: Any geo match (regardless of company)
                logger.info("🔍 Strategy 2: Matching by GEO only (any company)")
                for wl in wishlists:
                    wl_geos = geo_set(get_field_value(wl, 'geo'))
                    if has_geo_match(geo_norm, wl_geos):
                        for off in offers:
                            off_geos = geo_set(get_field_value(off, 'geo'))
                            if has_geo_match(geo_norm, off_geos):
                                pair_id = (off.id, wl.id)
                                if pair_id not in seen_pairs:
                                    matches.append({
                                        'wishlist': wl, 
                                        'offer': off,
                                        'match_reason': f"Geo match: {geo_norm}",
                                        'match_type': 'geo_only'
                                    })
                                    seen_pairs.add(pair_id)
                                    MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                    logger.info(f"✅ Geo Match: Offer '{off.campaign_name}' with wishlist")
            
            # CASE 3: BOTH offer_name and geo are provided
            elif offer_name_norm and geo_norm:
                logger.info(f"🎯 Search Mode: BOTH OFFER NAME AND GEO")
                
                # Try THREE matching strategies in order of priority:
                # 1. Company + Offer Name (partial) + Geo (perfect match)
                # 2. Offer Name (partial) + Geo (companies may differ)
                # 3. Company + Geo (offer names may differ)
                
                # STRATEGY 1: Company + Offer Name (partial) + Geo
                logger.info("🔍 Strategy 1: Company + Offer Name (partial) + Geo")
                for company in common_companies:
                    for off in advertiser_companies.get(company, []):
                        off_name = norm(get_field_value(off, 'campaign_name'))
                        off_geos = geo_set(get_field_value(off, 'geo'))
                        
                        if contains_partial(offer_name_norm, off_name) and has_geo_match(geo_norm, off_geos):
                            for wl in publisher_companies.get(company, []):
                                wl_name = norm(get_field_value(wl, 'desired_campaign'))
                                wl_geos = geo_set(get_field_value(wl, 'geo'))
                                
                                if contains_partial(offer_name_norm, wl_name) and has_geo_match(geo_norm, wl_geos):
                                    pair_id = (off.id, wl.id)
                                    if pair_id not in seen_pairs:
                                        matches.append({
                                            'wishlist': wl, 
                                            'offer': off,
                                            'match_reason': f"Company '{company}', offer name contains '{offer_name_norm}', geo '{geo_norm}'",
                                            'match_type': 'company_name_geo'
                                        })
                                        seen_pairs.add(pair_id)
                                        MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                        logger.info(f"✅ Company+Name+Geo Match: {company}, contains '{offer_name_norm}', {geo_norm}")
                
                # STRATEGY 2: Offer Name (partial) + Geo match (companies may differ)
                logger.info("🔍 Strategy 2: Offer Name (partial) + Geo match")
                for off in offers:
                    off_name = norm(get_field_value(off, 'campaign_name'))
                    off_geos = geo_set(get_field_value(off, 'geo'))
                    
                    if contains_partial(offer_name_norm, off_name) and has_geo_match(geo_norm, off_geos):
                        for wl in wishlists:
                            wl_name = norm(get_field_value(wl, 'desired_campaign'))
                            wl_geos = geo_set(get_field_value(wl, 'geo'))
                            
                            if contains_partial(offer_name_norm, wl_name) and has_geo_match(geo_norm, wl_geos):
                                pair_id = (off.id, wl.id)
                                if pair_id not in seen_pairs:
                                    # Check if companies also match
                                    off_company = norm(off.advertiser.company_name) if off.advertiser and off.advertiser.company_name else ''
                                    wl_company = norm(wl.publisher.company_name) if wl.publisher and wl.publisher.company_name else ''
                                    
                                    if off_company == wl_company and off_company:
                                        match_type = 'company_name_geo'
                                        match_reason = f"Company '{off_company}' + name contains '{offer_name_norm}' + geo '{geo_norm}'"
                                    else:
                                        match_type = 'name_geo'
                                        match_reason = f"Offer name contains '{offer_name_norm}' + geo '{geo_norm}' (companies differ)"
                                    
                                    matches.append({
                                        'wishlist': wl, 
                                        'offer': off,
                                        'match_reason': match_reason,
                                        'match_type': match_type
                                    })
                                    seen_pairs.add(pair_id)
                                    MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                    logger.info(f"✅ {match_type.upper()} Match: contains '{offer_name_norm}', {geo_norm}")
                
                # STRATEGY 3: Company + Geo match (offer names may differ)
                logger.info("🔍 Strategy 3: Company + Geo match")
                for company in common_companies:
                    for off in advertiser_companies.get(company, []):
                        off_geos = geo_set(get_field_value(off, 'geo'))
                        if has_geo_match(geo_norm, off_geos):
                            for wl in publisher_companies.get(company, []):
                                wl_geos = geo_set(get_field_value(wl, 'geo'))
                                if has_geo_match(geo_norm, wl_geos):
                                    pair_id = (off.id, wl.id)
                                    if pair_id not in seen_pairs:
                                        matches.append({
                                            'wishlist': wl, 
                                            'offer': off,
                                            'match_reason': f"Company '{company}' + geo '{geo_norm}'",
                                            'match_type': 'company_geo'
                                        })
                                        seen_pairs.add(pair_id)
                                        MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                                        logger.info(f"✅ Company+Geo Match: {company}, {geo_norm}")
            
            # CASE 4: NEITHER offer_name nor geo provided
            elif not offer_name_norm and not geo_norm:
                logger.info("🔗 Search Mode: MATCH ALL")
                
                # Match based on company first
                for company in common_companies:
                    for off in advertiser_companies.get(company, []):
                        for wl in publisher_companies.get(company, []):
                            pair_id = (off.id, wl.id)
                            if pair_id not in seen_pairs:
                                matches.append({
                                    'wishlist': wl, 
                                    'offer': off,
                                    'match_reason': f"Company match: {company}",
                                    'match_type': 'company_only'
                                })
                                seen_pairs.add(pair_id)
                                MatchHistory.objects.get_or_create(offer=off, wishlist=wl)
                
                logger.info(f"🔗 Found {len(matches)} company-based matches")
        
        except Exception as e:
            logger.error(f"❌ Error during manual match: {e}", exc_info=True)
            raise

        logger.info(f"✅ Manual match completed: {len(matches)} matches found")
        return matches

    def _calculate_match_score(self, offer, wishlist):
        """Calculate a match score based on how many fields match"""
        score = 0
        total_fields = 0
        
        field_pairs = [
            ('campaign_name', 'desired_campaign'),
            ('geo', 'geo'),
            ('payout', 'desired_payout'),
            ('kpi', 'desired_kpi'),
            ('model', 'desired_model'),
            ('vertical', 'desired_vertical')
        ]
        
        for offer_field, wishlist_field in field_pairs:
            total_fields += 1
            offer_val = getattr(offer, offer_field, None)
            wishlist_val = getattr(wishlist, wishlist_field, None)
            
            if offer_val and wishlist_val:
                if str(offer_val).strip().lower() == str(wishlist_val).strip().lower():
                    score += 1
                elif not offer_val or not wishlist_val:
                    # One is empty - partial match
                    score += 0.5
        
        # Add company match bonus
        if (offer.advertiser and offer.advertiser.company_name and 
            wishlist.publisher and wishlist.publisher.company_name and
            offer.advertiser.company_name.strip().lower() == wishlist.publisher.company_name.strip().lower()):
            score += 2
        
        return round((score / total_fields) * 100, 1) if total_fields > 0 else 0

    def get(self, request, *args, **kwargs):
        """Handle GET requests - Display empty matcher page with today's match history"""
        today = timezone.now().date()
        today_match_history = MatchHistory.objects.select_related(
            'offer', 'wishlist', 'wishlist__publisher', 'offer__advertiser'
        ).filter(
            matched_at__date=today
        ).order_by('-matched_at')[:50]

        # Get search parameters from GET if any
        offer_name_q = request.GET.get('offer_name', '').strip()
        geo_q = request.GET.get('geo', '').strip()
        
        matches = []
        if offer_name_q or geo_q:
            # Perform search if parameters exist
            matches = self._perform_manual_match(offer_name_q, geo_q)

        context = self.get_context_data(
            matches=matches,
            match_history=today_match_history,
            start_date='',
            end_date='',
            offer_name=offer_name_q,
            geo=geo_q,
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

            logger.info(f"📊 Search Result - Found {len(matches)} matches")

            # Get today's match history to include in response
            today = timezone.now().date()
            today_match_history = MatchHistory.objects.select_related(
                'offer', 'wishlist', 'wishlist__publisher', 'offer__advertiser'
            ).filter(
                matched_at__date=today
            ).order_by('-matched_at')[:20]
            
            # Build history HTML
            history_html = self._build_history_html(today_match_history)

            # Build match results HTML
            results_html = self._build_match_results_html(matches)

            # Combine both
            html = f"""
            <div class="row">
                <div class="col-12">
                    {results_html}
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-12">
                    <h5 class="fw-bold mb-3 text-primary"><i class="bi bi-clock-history"></i> Today's Match History</h5>
                    {history_html}
                </div>
            </div>
            """

            return JsonResponse({
                'html': html, 
                'status': 'success',
                'match_count': len(matches)
            })

        except Exception as e:
            logger.exception(f"❌ Error in POST request: {e}")
            error_msg = f"Server error: {str(e)}"
            return JsonResponse({
                'html': f'<div class="alert alert-danger"><strong>Error:</strong> {error_msg}</div>',
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    def _build_history_html(self, match_history):
        """Build HTML for match history section"""
        if not match_history:
            return '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No matches recorded today.</div>'
        
        html_parts = []
        html_parts.append('<div class="table-responsive">')
        html_parts.append('<table class="table table-sm table-hover">')
        html_parts.append('<thead class="table-light">')
        html_parts.append('<tr><th>Time</th><th>Offer</th><th>Publisher</th></tr>')
        html_parts.append('</thead><tbody>')
        
        for h in match_history:
            time_str = h.matched_at.strftime('%H:%M:%S')
            offer_name = h.offer.campaign_name or '-'
            publisher_name = h.wishlist.publisher.company_name if h.wishlist.publisher else '-'
            
            html_parts.append(
                f'<tr>'
                f'<td>{time_str}</td>'
                f'<td>{offer_name}</td>'
                f'<td>{publisher_name}</td>'
                f'</tr>'
            )
        
        html_parts.append('</tbody></table></div>')
        return ''.join(html_parts)
                
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