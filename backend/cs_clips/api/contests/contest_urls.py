from django.urls import path
from cs_clips.api.contests.contest_views import ContestWinnersView, EndContestView

urlpatterns = [
    path('contests/winners/', ContestWinnersView.as_view(), name='contest-winners'),
    path('contests/end/', EndContestView.as_view(), name='contest-end'),
]
