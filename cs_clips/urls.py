# urls con le View
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, VideoViewSet, RatingViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]