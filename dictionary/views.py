import requests
from django.shortcuts import render
from django.http import Http404
from core.ai_fallback import get_agronomic_info

def crop_list(request):
    query = request.GET.get('q', 'Farming')
    # Default search to 'Farming' to have initial population
    
    headers = {'User-Agent': 'AgriPath/1.0 (test@agripath.in)'}
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=12&namespace=0&format=json"
    
    crops = []
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            titles = data[1]
            links = data[3]
            for i in range(len(titles)):
                crops.append({'title': titles[i], 'url': links[i]})
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        
    return render(request, 'dictionary/crop_list.html', {'crops': crops, 'query': query})

def crop_detail(request, title):
    headers = {'User-Agent': 'AgriPath/1.0 (test@agripath.in)'}
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    
    try:
        response = requests.get(summary_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            crop = {
                'title': data.get('title', title),
                'description': data.get('extract_html', 'No description found.'),
                'image_url': data.get('thumbnail', {}).get('source', None),
                'wikipedia_url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
            }
        else:
            raise Http404("Crop article not found on Wikipedia")
            
        # Fetch structured Agronomic Information using the generative AI model
        agronomy_html = get_agronomic_info(title)
        
    except Exception as e:
        raise Http404(f"Error fetching data: {e}")
        
    return render(request, 'dictionary/crop_detail.html', {'crop': crop, 'agronomy_html': agronomy_html})
