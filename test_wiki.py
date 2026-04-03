import requests
import json

headers = {'User-Agent': 'AgriPathBot/1.0 (test@agripath.in)'}
url = 'https://en.wikipedia.org/api/rest_v1/page/summary/Tomato'
response = requests.get(url, headers=headers)
print(json.dumps(response.json(), indent=2))
