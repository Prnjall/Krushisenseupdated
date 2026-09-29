import json
import math
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from .models import KVK

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometres
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def serialize_kvk(kvk, distance=None):
    data = {
        "id": str(kvk.id),
        "official_id": kvk.official_id,
        "name": kvk.name,
        "state": kvk.state,
        "district": kvk.district,
        "atari_zone": kvk.atari_zone,
        "host_organization": kvk.host_organization,
        "host_organization_type": kvk.host_organization_type,
        "address": kvk.address,
        "phone": kvk.phone,
        "email": kvk.email,
        "website": kvk.website,
        "latitude": kvk.latitude,
        "longitude": kvk.longitude,
        "services": {
            "has_soil_testing": kvk.has_soil_testing,
            "has_mobile_lab": kvk.has_mobile_lab,
            "offers_expert_consultation": kvk.offers_expert_consultation,
            "soil_testing_price_min": float(kvk.soil_testing_price_min) if kvk.soil_testing_price_min is not None else None,
            "soil_testing_price_max": float(kvk.soil_testing_price_max) if kvk.soil_testing_price_max is not None else None,
        },
        "is_active": kvk.is_active,
    }
    if distance is not None:
        data["distance_km"] = round(distance, 2)
    return data

@require_GET
def list_kvks_view(request):
    queryset = KVK.objects.all()

    # Filters
    state = request.GET.get('state')
    district = request.GET.get('district')
    search = request.GET.get('search')
    is_active_param = request.GET.get('is_active')

    if state:
        queryset = queryset.filter(state__iexact=state)
    if district:
        queryset = queryset.filter(district__iexact=district)
    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(district__icontains=search))
    
    if is_active_param is not None:
        if is_active_param.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active_param.lower() == 'false':
            queryset = queryset.filter(is_active=False)
    else:
        # Default to active only if not specified
        queryset = queryset.filter(is_active=True)

    # Ordering
    queryset = queryset.order_by('state', 'district', 'name')

    # Pagination
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        if page < 1:
            return JsonResponse({"success": False, "error": "Page must be at least 1"}, status=400)
        if limit < 1:
            return JsonResponse({"success": False, "error": "Limit must be at least 1"}, status=400)
        if limit > 100:
            limit = 100
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid pagination parameters"}, status=400)

    total = queryset.count()
    start = (page - 1) * limit
    end = start + limit
    
    kvks = queryset[start:end]
    results = [serialize_kvk(k) for k in kvks]

    return JsonResponse({
        "success": True,
        "data": results,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": math.ceil(total / limit) if limit > 0 else 0
        }
    })

@require_GET
def nearest_kvk_view(request):
    try:
        lat = float(request.GET.get('latitude'))
        lng = float(request.GET.get('longitude'))
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid or missing latitude/longitude"}, status=400)

    if not (-90 <= lat <= 90):
        return JsonResponse({"success": False, "error": "Latitude out of bounds"}, status=400)
    if not (-180 <= lng <= 180):
        return JsonResponse({"success": False, "error": "Longitude out of bounds"}, status=400)

    try:
        limit = int(request.GET.get('limit', 5))
        if limit < 1:
            return JsonResponse({"success": False, "error": "Limit must be at least 1"}, status=400)
        if limit > 50:
            limit = 50
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid limit parameter"}, status=400)

    # Fetch active KVKs with coordinates
    # We load them into memory since we're using SQLite.
    # The dataset is small (~731 records), so calculating Haversine in Python is O(N) and extremely fast.
    # For large datasets (millions), a bounding box pre-filter or PostGIS would be necessary.
    active_kvks = KVK.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False)
    
    distances = []
    for kvk in active_kvks:
        dist = haversine_distance(lat, lng, kvk.latitude, kvk.longitude)
        distances.append((dist, kvk))
        
    distances.sort(key=lambda x: x[0])
    
    nearest = distances[:limit]
    
    results = [serialize_kvk(k, distance=dist) for dist, k in nearest]

    return JsonResponse({
        "success": True,
        "data": results
    })
