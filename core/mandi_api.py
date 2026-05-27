import requests
import time
from django.conf import settings

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MANDI_API_KEY = getattr(settings, 'MANDI_API_KEY', None)
RESOURCE_ID = '9ef84268-d588-465a-a308-a864a43d0070'
BASE_URL = f'https://api.data.gov.in/resource/{RESOURCE_ID}'

# A small set of mainstream crops always shown on the ticker regardless of what the user tracks.
# Keep this list SHORT — each entry is a separate API call.
DEFAULT_CROPS = [
    'Wheat', 'Rice', 'Tomato', 'Onion', 'Potato',
]

# Maps common user-typed names → exact Agmarknet commodity name.
COMMODITY_ALIASES = {
    # Sugarcane
    'Sugarcane':        'Sugarcane Jaggery',
    'Sugar Cane':       'Sugarcane Jaggery',
    'Ganna':            'Sugarcane Jaggery',
    'Gur':              'Sugarcane Jaggery',
    'Jaggery':          'Sugarcane Jaggery',
    # Cereals
    'Paddy':            'Paddy(Dhan)(Common)',
    'Dhaan':            'Paddy(Dhan)(Common)',
    'Dhan':             'Paddy(Dhan)(Common)',
    'Basmati':          'Rice',
    'Gehu':             'Wheat',
    'Jowar':            'Jowar(Sorghum)',
    'Sorghum':          'Jowar(Sorghum)',
    'Bajra':            'Bajra(Pearl Millet/Cumbu)',
    'Pearl Millet':     'Bajra(Pearl Millet/Cumbu)',
    'Ragi':             'Ragi (Finger Millet)',
    'Finger Millet':    'Ragi (Finger Millet)',
    'Nachni':           'Ragi (Finger Millet)',
    'Barley':           'Barley (Jau)',
    'Jau':              'Barley (Jau)',
    # Pulses
    'Tur':              'Arhar (Tur/Red Gram)(Whole)',
    'Arhar':            'Arhar (Tur/Red Gram)(Whole)',
    'Red Gram':         'Arhar (Tur/Red Gram)(Whole)',
    'Toor Dal':         'Arhar (Tur/Red Gram)(Whole)',
    'Moong':            'Moong (Green Gram)(Whole)',
    'Green Gram':       'Moong (Green Gram)(Whole)',
    'Mung':             'Moong (Green Gram)(Whole)',
    'Urad':             'Urad (Black Matpe)(Whole)',
    'Black Gram':       'Urad (Black Matpe)(Whole)',
    'Masur':            'Lentil (Masur)(Whole)',
    'Masoor':           'Lentil (Masur)(Whole)',
    'Lentil':           'Lentil (Masur)(Whole)',
    'Rajma':            'Rajma',
    'Kidney Beans':     'Rajma',
    'Moth':             'Moth(Whole)',
    'Horse Gram':       'Kulthi(Horse Gram)',
    'Kulthi':           'Kulthi(Horse Gram)',
    # Oilseeds
    'Soya':             'Soyabean',
    'Soy':              'Soyabean',
    'Sarson':           'Mustard',
    'Rai':              'Mustard',
    'Makka':            'Maize',
    'Corn':             'Maize',
    'Sunflower Seeds':  'Sunflower',
    'Surajmukhi':       'Sunflower',
    'Groundnut Pods':   'Groundnut',
    'Moongphali':       'Groundnut',
    'Peanut':           'Groundnut',
    'Sesame':           'Sesame(Gingelly)',
    'Til':              'Sesame(Gingelly)',
    'Gingelly':         'Sesame(Gingelly)',
    'Niger Seed':       'Niger Seed (Ramtil)',
    'Ramtil':           'Niger Seed (Ramtil)',
    'Linseed':          'Linseed',
    'Alsi':             'Linseed',
    'Castor':           'Castor Seed',
    'Arandi':           'Castor Seed',
    # Spices & Condiments
    'Tamatar':          'Tomato',
    'Pyaz':             'Onion',
    'Aloo':             'Potato',
    'Haldi':            'Turmeric',
    'Adrak':            'Ginger(Dry)',
    'Ginger':           'Ginger(Dry)',
    'Mirch':            'Chilly Red',
    'Chilli':           'Chilly Red',
    'Red Chilli':       'Chilly Red',
    'Lahsun':           'Garlic',
    'Dhaniya':          'Coriander(Leaves)',
    'Coriander':        'Coriander(Leaves)',
    'Saunf':            'Dill(Suva/Soya)',
    'Dill':             'Dill(Suva/Soya)',
    # Vegetables
    'Lady Finger':      'Ladyfinger(Bhindi)',
    'Bhindi':           'Ladyfinger(Bhindi)',
    'Okra':             'Ladyfinger(Bhindi)',
    'Baingan':          'Brinjal',
    'Eggplant':         'Brinjal',
    'Gobhi':            'Cauliflower',
    'Patta Gobhi':      'Cabbage',
    'Shimla Mirch':     'Capsicum',
    'Bell Pepper':      'Capsicum',
    'Kaddu':            'Bottle Gourd',
    'Lauki':            'Bottle Gourd',
    'Karela':           'Bitter Gourd',
    'Kheera':           'Cucumber',
    'Palak':            'Spinach(Palak)',
    'Spinach':          'Spinach(Palak)',
    'Methi':            'Methi(Leaves)',
    'Fenugreek':        'Methi(Leaves)',
    'Gajar':            'Carrot',
    'Mooli':            'Radish',
    'Chukander':        'Beet Root',
    'Beetroot':         'Beet Root',
    'Sahjan':           'Drumstick',
    'Moringa':          'Drumstick',
    'Guar':             'Cluster Beans',
    # Fruits
    'Kela':             'Banana',
    'Aam':              'Mango',
    'Amrud':            'Guava',
    'Santra':           'Orange',
    'Papita':           'Papaya',
    'Angur':            'Grapes',
    'Anar':             'Pomegranate',
    'Seb':              'Apple',
    'Tarbuz':           'Watermelon',
    'Kharbuja':         'Muskmelon',
    'Nariyal':          'Coconut',
    'Supari':           'Arecanut(Betelnut/Supari)',
    'Arecanut':         'Arecanut(Betelnut/Supari)',
    'Betelnut':         'Arecanut(Betelnut/Supari)',
}

# In-process cache: { lookup_name: (timestamp, price_data_or_None) }
# Only successful results are cached (no negative caching).
_cache = {}
CACHE_TTL = 3600  # 1 hour


def get_mandi_prices(crop_names):
    """
    Fetch live wholesale prices from data.gov.in/Agmarknet for a list of crop names.

    Returns: { display_name: {'min':X, 'max':Y, 'modal':Z, 'market':'...', 'state':'...'} }
    Crops with no matching Agmarknet entry are silently omitted.
    """
    if not MANDI_API_KEY:
        return {}

    result = {}
    now = time.time()

    for raw_name in crop_names:
        user_name = raw_name.strip().title()
        if not user_name:
            continue

        # Apply alias mapping
        lookup_name = COMMODITY_ALIASES.get(user_name, user_name)
        # Display label: use alias target so ticker shows "Sugarcane Jaggery" not "Sugarcane"
        display_name = lookup_name

        # Cache hit?
        if lookup_name in _cache:
            cached_ts, cached_data = _cache[lookup_name]
            if now - cached_ts < CACHE_TTL and cached_data:
                result[display_name] = cached_data
                continue

        # Fetch from API
        params = {
            'api-key': MANDI_API_KEY,
            'format': 'json',
            'filters[commodity]': lookup_name,
            'limit': 5,
        }
        try:
            resp = requests.get(BASE_URL, params=params, timeout=2)
            if resp.status_code == 200:
                records = resp.json().get('records', [])
                if records:
                    r = records[0]
                    price_data = {
                        'min':    int(r.get('min_price',   0)),
                        'max':    int(r.get('max_price',   0)),
                        'modal':  int(r.get('modal_price', 0)),
                        'market': r.get('market', 'N/A'),
                        'state':  r.get('state', 'N/A'),
                        'date':   r.get('arrival_date', ''),
                    }
                    _cache[lookup_name] = (now, price_data)
                    result[display_name] = price_data
                # else: don't cache empty — will retry on next page load
            else:
                print(f"Mandi API {resp.status_code} for '{lookup_name}'")
        except Exception as e:
            print(f"Mandi API error for '{lookup_name}': {e}")

    return result
