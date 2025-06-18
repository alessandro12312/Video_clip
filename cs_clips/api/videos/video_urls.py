from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cs_clips.api.videos.video_views import VideoViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')

urlpatterns = [
    path('', include(router.urls)),
]
