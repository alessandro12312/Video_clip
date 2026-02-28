from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cs_clips.api.videos.video_views import VideoViewSet

router = DefaultRouter()
router.register(r"videos", VideoViewSet, basename="video")

urlpatterns = [
    path("", include(router.urls)),
]
