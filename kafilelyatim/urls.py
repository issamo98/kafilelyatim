# project/urls.py
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
]
