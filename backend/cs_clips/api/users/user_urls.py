from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cs_clips.api.users.user_views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
