# urls con le View
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cs_clips.api.brackets.bracket_views import BracketViewSet, MatchupViewSet
from cs_clips.api.comments.comment_views import CommentViewSet
from cs_clips.api.contests.contest_views import ContestViewSet
from cs_clips.api.notifications.notification_views import NotificationViewSet
from cs_clips.api.ratings.rating_views import RatingViewSet
from cs_clips.api.users.user_views import UserViewSet
from cs_clips.api.videos.video_views import VideoViewSet

# Si usa per le viewset che gestiscono CRUD standard
router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"videos", VideoViewSet)
router.register(r"ratings", RatingViewSet)
router.register(r"comments", CommentViewSet)
router.register(r"contests", ContestViewSet, basename="contest")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"brackets", BracketViewSet, basename="bracket")
router.register(r"matchups", MatchupViewSet, basename="matchup")

urlpatterns = [
    path("", include(router.urls)),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
