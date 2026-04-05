import requests, json
api_key = '579b464db66ec23bdd0000013f635a432d4041c873c36cf228452261'
resource_id = '9ef84268-d588-465a-a308-a864a43d0070'
url = f'https://api.data.gov.in/resource/{resource_id}'

for name in ['Sugarcane', 'Sugar Cane', 'Sugarcane Jaggery']:
    r = requests.get(url, params={'api-key': api_key, 'format': 'json', 'filters[commodity]': name, 'limit': 1}, timeout=8)
    data = r.json()
    records = data.get('records', [])
    print(f"'{name}' → {len(records)} record(s) {records[0] if records else 'NOT FOUND'}")
