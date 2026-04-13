import requests
from django.core.cache import cache
from django.conf import settings


def get_agri_news():
    """
    Fetches latest news relevant to Indian farmers in English using NewsData.io.
    Caches the results for 6 hours (21600 seconds) to avoid hitting the free tier limits (200/day).
    """
    CACHE_KEY = 'agri_news_en_strict_v6'
    cached_news = cache.get(CACHE_KEY)

    if cached_news is not None:
        return cached_news

    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    if not api_key:
        return []

    url = "https://newsdata.io/api/1/latest"
    params = {
        "apikey": api_key,
        "q": "agriculture AND (farmer OR crops OR MSP OR policy)",
        "language": "en",
        "country": "in"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Limit to 9 articles to keep the UI clean and fast
        results = data.get("results", [])[:9]

        # Clean up results (remove empty images or missing URLs if necessary, though template can handle it)
        cleaned_results = []
        for item in results:
            cleaned_results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "image_url": item.get("image_url"),
                "description": item.get("description"),
                "content": item.get("description"),  # NewsData puts paid warning in 'content'. Use 'description' instead.
                "pubDate": item.get("pubDate"),
                "source_id": item.get("source_id"),
            })

        cache.set(CACHE_KEY, cleaned_results, 21600)
        return cleaned_results

    except requests.exceptions.Timeout:
        return []
    except Exception:
        return []
