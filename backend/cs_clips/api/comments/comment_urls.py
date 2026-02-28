from django.urls import path, include

urlpatterns = [
    path('', include('cs_clips.api.users.urls')),
    path('', include('cs_clips.api.videos.urls')),
    path('', include('cs_clips.api.comments.urls')),
    path('', include('cs_clips.api.ratings.urls')),
    path('', include('cs_clips.api.contests.urls')),
]
