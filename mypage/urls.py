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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('ai', core_views.assistant_page, name='ai'), # Serve the HTML page at root
    path('process/', core_views.process_voice, name='process_voice'), # API endpoint
    path('api/get-greeting/', core_views.get_greeting, name='get_greeting'),
]
