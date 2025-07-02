# urls con le View
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cs_clips.api.comments.comment_views import CommentViewSet
from cs_clips.api.contests.contest_views import ContestWinnersView, EndContestView
from cs_clips.api.ratings.rating_views import RatingViewSet
from cs_clips.api.users.user_views import UserViewSet
from cs_clips.api.videos.video_views import VideoViewSet
from project_clip import settings
from django.conf.urls.static import static


# Si usa per le viewset che gestiscono CRUD standard
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Endpoint custom fuori dal router per i vincitori dei contest
    # Si usa per gli endpoint che non sono CRUD standard
    path('contests/winners/', ContestWinnersView.as_view(), name='contest-winners'),
    path('contests/end/', EndContestView.as_view(), name='contest-end'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)