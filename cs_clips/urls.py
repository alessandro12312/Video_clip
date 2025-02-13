# urls con le View
from django.urls import path
from .views import UserDetailView, UserCreateView, VideoUploadView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('videos/', VideoUploadView.as_view(), name='video_upload'),
]