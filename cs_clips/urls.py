from django.urls import path
from .views import RegisterUserView, VideoUploadView

urlpatterns = [
    path('api/register/', RegisterUserView.as_view(), name='api_register'),
    path('api/videos/', VideoUploadView.as_view(), name='api_video_upload'),
]