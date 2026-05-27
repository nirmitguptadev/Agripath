import requests
import time
from django.conf import settings

MANDI_API_KEY = getattr(settings, 'MANDI_API_KEY', None)
RESOURCE_ID = '9ef84268-d588-465a-a308-a864a43d0070'
BASE_URL = f'https://api.data.gov.in/resource/{RESOURCE_ID}'

DEFAULT_CROPS = ['Wheat', 'Rice', 'Tomato', 'Onion', 'Potato']

COMMODITY_ALIASES = {
    'Sugarcane': 'Sugarcane Jaggery', 'Sugar Cane': 'Sugarcane Jaggery',
    'Ganna': 'Sugarcane Jaggery', 'Gur': 'Sugarcane Jaggery', 'Jaggery': 'Sugarcane Jaggery',
    'Paddy': 'Paddy(Dhan)(Common)', 'Dhaan': 'Paddy(Dhan)(Common)', 'Dhan': 'Paddy(Dhan)(Common)',
    'Basmati': 'Rice', 'Gehu': 'Wheat',
    'Jowar': 'Jowar(Sorghum)', 'Sorghum': 'Jowar(Sorghum)',
    'Bajra': 'Bajra(Pearl Millet/Cumbu)', 'Pearl Millet': 'Bajra(Pearl Millet/Cumbu)',
    'Ragi': 'Ragi (Finger Millet)', 'Finger Millet': 'Ragi (Finger Millet)', 'Nachni': 'Ragi (Finger Millet)',
    'Barley': 'Barley (Jau)', 'Jau': 'Barley (Jau)',
    'Tur': 'Arhar (Tur/Red Gram)(Whole)', 'Arhar': 'Arhar (Tur/Red Gram)(Whole)',
    'Red Gram': 'Arhar (Tur/Red Gram)(Whole)', 'Toor Dal': 'Arhar (Tur/Red Gram)(Whole)',
    'Moong': 'Moong (Green Gram)(Whole)', 'Green Gram': 'Moong (Green Gram)(Whole)', 'Mung': 'Moong (Green Gram)(Whole)',
    'Urad': 'Urad (Black Matpe)(Whole)', 'Black Gram': 'Urad (Black Matpe)(Whole)',
    'Masur': 'Lentil (Masur)(Whole)', 'Masoor': 'Lentil (Masur)(Whole)', 'Lentil': 'Lentil (Masur)(Whole)',
    'Rajma': 'Rajma', 'Kidney Beans': 'Rajma',
    'Moth': 'Moth(Whole)', 'Horse Gram': 'Kulthi(Horse Gram)', 'Kulthi': 'Kulthi(Horse Gram)',
    'Soya': 'Soyabean', 'Soy': 'Soyabean',
    'Sarson': 'Mustard', 'Rai': 'Mustard',
    'Makka': 'Maize', 'Corn': 'Maize',
    'Sunflower Seeds': 'Sunflower', 'Surajmukhi': 'Sunflower',
    'Groundnut Pods': 'Groundnut', 'Moongphali': 'Groundnut', 'Peanut': 'Groundnut',
    'Sesame': 'Sesame(Gingelly)', 'Til': 'Sesame(Gingelly)', 'Gingelly': 'Sesame(Gingelly)',
    'Niger Seed': 'Niger Seed (Ramtil)', 'Ramtil': 'Niger Seed (Ramtil)',
    'Linseed': 'Linseed', 'Alsi': 'Linseed',
    'Castor': 'Castor Seed', 'Arandi': 'Castor Seed',
    'Tamatar': 'Tomato', 'Pyaz': 'Onion', 'Aloo': 'Potato',
    'Haldi': 'Turmeric', 'Adrak': 'Ginger(Dry)', 'Ginger': 'Ginger(Dry)',
    'Mirch': 'Chilly Red', 'Chilli': 'Chilly Red', 'Red Chilli': 'Chilly Red',
    'Lahsun': 'Garlic', 'Dhaniya': 'Coriander(Leaves)', 'Coriander': 'Coriander(Leaves)',
    'Saunf': 'Dill(Suva/Soya)', 'Dill': 'Dill(Suva/Soya)',
    'Lady Finger': 'Ladyfinger(Bhindi)', 'Bhindi': 'Ladyfinger(Bhindi)', 'Okra': 'Ladyfinger(Bhindi)',
    'Baingan': 'Brinjal', 'Eggplant': 'Brinjal',
    'Gobhi': 'Cauliflower', 'Patta Gobhi': 'Cabbage',
    'Shimla Mirch': 'Capsicum', 'Bell Pepper': 'Capsicum',
    'Kaddu': 'Bottle Gourd', 'Lauki': 'Bottle Gourd',
    'Karela': 'Bitter Gourd', 'Kheera': 'Cucumber',
    'Palak': 'Spinach(Palak)', 'Spinach': 'Spinach(Palak)',
    'Methi': 'Methi(Leaves)', 'Fenugreek': 'Methi(Leaves)',
    'Gajar': 'Carrot', 'Mooli': 'Radish',
    'Chukander': 'Beet Root', 'Beetroot': 'Beet Root',
    'Sahjan': 'Drumstick', 'Moringa': 'Drumstick',
    'Guar': 'Cluster Beans',
    'Kela': 'Banana', 'Aam': 'Mango', 'Amrud': 'Guava', 'Santra': 'Orange',
    'Papita': 'Papaya', 'Angur': 'Grapes', 'Anar': 'Pomegranate', 'Seb': 'Apple',
    'Tarbuz': 'Watermelon', 'Kharbuja': 'Muskmelon', 'Nariyal': 'Coconut',
    'Supari': 'Arecanut(Betelnut/Supari)', 'Arecanut': 'Arecanut(Betelnut/Supari)',
    'Betelnut': 'Arecanut(Betelnut/Supari)',
}

# In-process cache: stores the full bulk result dict + timestamp
# This survives for the lifetime of the worker process (avoids repeated API calls)
_bulk_cache = None       # { lookup_name: price_data }
_bulk_cache_ts = 0
CACHE_TTL = 3600  # 1 hour


def _fetch_bulk(lookup_names):
    """
    Fetch prices for all requested crops in as few API calls as possible.
    Uses a single request with a high limit — one network call instead of N.
    Falls back to the stale cache if the API is unreachable.
    """
    global _bulk_cache, _bulk_cache_ts

    if not MANDI_API_KEY:
        return {}

    now = time.time()

    # Return in-process cache if still fresh
    if _bulk_cache is not None and (now - _bulk_cache_ts) < CACHE_TTL:
        return _bulk_cache

    # Try Django's DB cache (survives worker restarts)
    try:
        from django.core.cache import cache
        cached = cache.get('mandi_bulk_prices')
        if cached:
            _bulk_cache = cached
            _bulk_cache_ts = now
            return _bulk_cache
    except Exception:
        pass

    # Fetch from API — single request, large limit
    try:
        params = {
            'api-key': MANDI_API_KEY,
            'format': 'json',
            'limit': 500,
        }
        resp = requests.get(BASE_URL, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"Mandi API returned {resp.status_code}")
            return _bulk_cache or {}

        records = resp.json().get('records', [])
        result = {}
        # Keep only the first (most recent) record per commodity
        for r in records:
            commodity = r.get('commodity', '')
            if commodity and commodity not in result:
                result[commodity] = {
                    'min':    int(r.get('min_price',   0) or 0),
                    'max':    int(r.get('max_price',   0) or 0),
                    'modal':  int(r.get('modal_price', 0) or 0),
                    'market': r.get('market', 'N/A'),
                    'state':  r.get('state',  'N/A'),
                    'date':   r.get('arrival_date', ''),
                }

        _bulk_cache = result
        _bulk_cache_ts = now

        # Store in Django DB cache for 1 hour (survives dyno restarts)
        try:
            from django.core.cache import cache
            cache.set('mandi_bulk_prices', result, CACHE_TTL)
        except Exception:
            pass

        return result

    except Exception as e:
        print(f"Mandi bulk fetch error: {e}")
        return _bulk_cache or {}


def get_mandi_prices(crop_names):
    """
    Returns: { display_name: {'min':X, 'max':Y, 'modal':Z, 'market':'...', 'state':'...'} }
    Also sets module-level `prices_are_fallback` flag.
    """
    lookup_names = []
    for raw in crop_names:
        user_name = raw.strip().title()
        if user_name:
            lookup_names.append(COMMODITY_ALIASES.get(user_name, user_name))

    bulk = _fetch_bulk(lookup_names)

    result = {}
    for raw in crop_names:
        user_name = raw.strip().title()
        if not user_name:
            continue
        lookup_name = COMMODITY_ALIASES.get(user_name, user_name)
        if lookup_name in bulk:
            result[lookup_name] = bulk[lookup_name]

    # If API returned nothing, use hardcoded fallback prices
    global prices_are_fallback
    if not result:
        prices_are_fallback = True
        for raw in crop_names:
            user_name = raw.strip().title()
            if not user_name:
                continue
            lookup_name = COMMODITY_ALIASES.get(user_name, user_name)
            if lookup_name in FALLBACK_PRICES:
                result[lookup_name] = FALLBACK_PRICES[lookup_name]
    else:
        prices_are_fallback = False

    return result


prices_are_fallback = False

# Last-known approximate wholesale prices (₹/quintal) — used when API is unreachable.
FALLBACK_PRICES = {
    'Wheat':                      {'min': 2100, 'max': 2400, 'modal': 2275, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Rice':                       {'min': 2200, 'max': 2600, 'modal': 2400, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Paddy(Dhan)(Common)':        {'min': 1800, 'max': 2200, 'modal': 2000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Maize':                      {'min': 1700, 'max': 2100, 'modal': 1900, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Bajra(Pearl Millet/Cumbu)':  {'min': 1800, 'max': 2200, 'modal': 2000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Jowar(Sorghum)':             {'min': 2000, 'max': 2500, 'modal': 2200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Ragi (Finger Millet)':       {'min': 2800, 'max': 3500, 'modal': 3100, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Barley (Jau)':               {'min': 1600, 'max': 2000, 'modal': 1800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Gram':                       {'min': 4500, 'max': 5500, 'modal': 5000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Moong (Green Gram)(Whole)':  {'min': 6500, 'max': 8000, 'modal': 7200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Urad (Black Matpe)(Whole)':  {'min': 6000, 'max': 7500, 'modal': 6800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Lentil (Masur)(Whole)':      {'min': 5000, 'max': 6500, 'modal': 5800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Arhar (Tur/Red Gram)(Whole)':{'min': 6000, 'max': 7500, 'modal': 6800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Rajma':                      {'min': 8000, 'max': 11000,'modal': 9500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Mustard':                    {'min': 4800, 'max': 5800, 'modal': 5300, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Soyabean':                   {'min': 3800, 'max': 4800, 'modal': 4300, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Groundnut':                  {'min': 4500, 'max': 6000, 'modal': 5200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Sunflower':                  {'min': 4500, 'max': 5500, 'modal': 5000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Sesame(Gingelly)':           {'min': 10000,'max': 14000,'modal': 12000,'market': 'Indicative', 'state': 'India', 'date': ''},
    'Castor Seed':                {'min': 5000, 'max': 6500, 'modal': 5800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Cotton':                     {'min': 5500, 'max': 7000, 'modal': 6200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Tomato':                     {'min': 800,  'max': 2500, 'modal': 1500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Onion':                      {'min': 600,  'max': 2000, 'modal': 1200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Potato':                     {'min': 700,  'max': 1800, 'modal': 1100, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Brinjal':                    {'min': 600,  'max': 2000, 'modal': 1200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Cauliflower':                {'min': 500,  'max': 1800, 'modal': 1000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Cabbage':                    {'min': 400,  'max': 1200, 'modal': 700,  'market': 'Indicative', 'state': 'India', 'date': ''},
    'Capsicum':                   {'min': 1500, 'max': 4000, 'modal': 2500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Ladyfinger(Bhindi)':         {'min': 1000, 'max': 3000, 'modal': 1800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Cucumber':                   {'min': 500,  'max': 1500, 'modal': 900,  'market': 'Indicative', 'state': 'India', 'date': ''},
    'Peas Green':                 {'min': 1500, 'max': 4000, 'modal': 2500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Carrot':                     {'min': 800,  'max': 2500, 'modal': 1500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Radish':                     {'min': 300,  'max': 1000, 'modal': 600,  'market': 'Indicative', 'state': 'India', 'date': ''},
    'Spinach(Palak)':             {'min': 500,  'max': 1500, 'modal': 900,  'market': 'Indicative', 'state': 'India', 'date': ''},
    'Methi(Leaves)':              {'min': 600,  'max': 2000, 'modal': 1100, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Turmeric':                   {'min': 7000, 'max': 12000,'modal': 9500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Garlic':                     {'min': 3000, 'max': 8000, 'modal': 5000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Ginger(Dry)':                {'min': 8000, 'max': 15000,'modal': 11000,'market': 'Indicative', 'state': 'India', 'date': ''},
    'Chilly Red':                 {'min': 8000, 'max': 15000,'modal': 11000,'market': 'Indicative', 'state': 'India', 'date': ''},
    'Coriander(Leaves)':          {'min': 1000, 'max': 3000, 'modal': 1800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Banana':                     {'min': 800,  'max': 2000, 'modal': 1300, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Mango':                      {'min': 2000, 'max': 6000, 'modal': 3500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Guava':                      {'min': 1000, 'max': 3000, 'modal': 1800, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Orange':                     {'min': 2000, 'max': 5000, 'modal': 3200, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Papaya':                     {'min': 500,  'max': 1500, 'modal': 900,  'market': 'Indicative', 'state': 'India', 'date': ''},
    'Grapes':                     {'min': 3000, 'max': 8000, 'modal': 5000, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Pomegranate':                {'min': 4000, 'max': 10000,'modal': 6500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Apple':                      {'min': 4000, 'max': 10000,'modal': 6500, 'market': 'Indicative', 'state': 'India', 'date': ''},
    'Watermelon':                 {'min': 300,  'max': 800,  'modal': 500,  'market': 'Indicative', 'state': 'India', 'date': ''},
    'Sugarcane Jaggery':          {'min': 3500, 'max': 5000, 'modal': 4200, 'market': 'Indicative', 'state': 'India', 'date': ''},
}
