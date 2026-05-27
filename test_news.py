#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypage.settings')
django.setup()

from core.news_api import get_agri_news

print("Testing News API...")
try:
    news_items = get_agri_news()
    print(f"Found {len(news_items)} news items")
    if news_items:
        print("\nFirst news item:")
        print(f"Title: {news_items[0].get('title', 'N/A')}")
        print(f"Source: {news_items[0].get('source_id', 'N/A')}")
        print(f"Description: {news_items[0].get('description', 'N/A')[:100]}...")
        print(f"Image URL: {news_items[0].get('image_url', 'N/A')}")
        print(f"Link: {news_items[0].get('link', 'N/A')}")
    else:
        print("No news items found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
