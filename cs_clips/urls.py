from django.urls import path
from .views import UserCreateView, VideoUploadView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('videos/', VideoUploadView.as_view(), name='video_upload'),
]