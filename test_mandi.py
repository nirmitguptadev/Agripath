import requests
import json
import urllib.parse

api_key = '579b464db66ec23bdd0000013f635a432d4041c873c36cf228452261'
resource_id = '9ef84268-d588-465a-a308-a864a43d0070' 
url = f"https://api.data.gov.in/resource/{resource_id}"

# Let's filter for just Tomato
params = {
    'api-key': api_key,
    'format': 'json',
    'filters[commodity]': 'Tomato',
    'limit': 5
}

try:
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("MANDI API RESPONSE FOR TOMATO (VEGETABLE):")
        print(json.dumps(data.get('records', []), indent=2))
    else:
        print(f"Error HTTP {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
