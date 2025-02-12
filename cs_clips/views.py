from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .models import VideoUpload
from .serializers import UserSerializer, VideoUploadSerializer

class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Registrazione avvenuta con successo", "user": UserSerializer(user).data}, status=201)
        return Response(serializer.errors, status=400)

class VideoUploadView(generics.ListCreateAPIView):
    serializer_class = VideoUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return VideoUpload.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)