from django.contrib import admin
from django.urls import path
from cs_clips.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]