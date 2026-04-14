"""
URL configuration for mypage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from core import views as core_views
from django.conf import settings        
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('home/', include('home.urls')),
    path('ai/', core_views.assistant_page, name='assistant_page'), 
    path('accounts/', include('accounts.urls')),
    path('dictionary/', include('dictionary.urls')),
    path('tracker/', include('tracker.urls')),
    path('process/', core_views.process_voice, name='process_voice'), 
    path('api/get-greeting/', core_views.get_greeting, name='get_greeting'),
    path('api/clear-chat/', core_views.clear_chat, name='clear_chat'),
    path('api/get-chat-history/', core_views.get_chat_history, name='get_chat_history'),
]

# Serve media files in both development and production
# (Crop images are application assets committed to git, not user uploads)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)