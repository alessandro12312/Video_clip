"""Test per endpoint feed following e thumbnail video (Story 2.3).

Copre: AC-1 (feed following paginato), AC-4 (thumbnail generazione e serving),
AC-5 (EmptyState), AC-6 (non-regressione).
"""

import shutil
import tempfile
from unittest.mock import MagicMock, patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
    create_toconfirm_user,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

MOCK_FILE_URL = "http://minio:9000/bucket/video.mp4?presigned=view"
MOCK_THUMBNAIL_URL = "http://minio:9000/bucket/thumbnails/thumb.jpg?presigned=view"


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestFeedFollowing(APITestCase):
    """Test endpoint GET /api/videos/following/ (AC-1, AC-5)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = create_authenticated_user("viewer")
        self.author1 = create_authenticated_user("author1")
        self.author2 = create_authenticated_user("author2")
        self.stranger = create_authenticated_user("stranger")

        # viewer segue author1 e author2
        self.user.following.add(self.author1, self.author2)

        # Crea video per i vari utenti
        self.video_a1 = create_sample_video(self.author1, title="Clip A1")
        self.video_a2 = create_sample_video(self.author2, title="Clip A2")
        self.video_stranger = create_sample_video(self.stranger, title="Clip Stranger")

        self.url = "/api/videos/following/"

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_feed_returns_only_following_videos(self, mock_minio):
        """Utente con following vede solo video dei following."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        client = create_api_client_authenticated(self.user)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [v["title"] for v in response.data["results"]]
        self.assertIn("Clip A1", titles)
        self.assertIn("Clip A2", titles)
        self.assertNotIn("Clip Stranger", titles)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_feed_empty_for_user_without_following(self, mock_minio):
        """Utente senza following vede lista vuota → 200 + formato paginato."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        loner = create_authenticated_user("loner")
        client = create_api_client_authenticated(loner)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data["count"], 0)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_feed_response_is_paginated(self, mock_minio):
        """Risposta è paginata (contiene count, next, previous, results)."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        client = create_api_client_authenticated(self.user)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_feed_ordered_by_created_at_descending(self, mock_minio):
        """Ordinamento per -created_at (il video più recente è primo)."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        # Crea un video più recente
        create_sample_video(self.author1, title="Newer Clip")

        client = create_api_client_authenticated(self.user)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["title"], "Newer Clip")

    def test_feed_unauthenticated_returns_401(self):
        """Utente non autenticato → 401."""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_feed_toconfirm_user_can_access(self, mock_minio):
        """Utente toconfirm può accedere al feed (lettura, paginata)."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        toconfirm = create_toconfirm_user()
        client = create_api_client_authenticated(toconfirm)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIsInstance(response.data["results"], list)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestThumbnailGeneration(APITestCase):
    """Test generazione thumbnail durante upload e serving via presigned URL (AC-4)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = create_authenticated_user("uploader")
        self.client_auth = create_api_client_authenticated(self.user)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_thumbnail_generated_during_upload(self, mock_vfc, mock_minio):
        """Generazione thumbnail durante upload — campo thumbnail viene popolato."""
        # Mock MoviePy: durata 30s + save_frame che crea un file JPEG finto
        mock_clip = MagicMock()
        mock_clip.duration = 30
        mock_clip.__enter__ = MagicMock(return_value=mock_clip)
        mock_clip.__exit__ = MagicMock(return_value=False)

        def fake_save_frame(path, t=0):
            # Crea un file JPEG finto
            with open(path, "wb") as f:
                f.write(b"\xff\xd8\xff\xe0fake-jpeg-content")

        mock_clip.save_frame = fake_save_frame
        mock_vfc.return_value = mock_clip

        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL

        from django.core.files.uploadedfile import SimpleUploadedFile

        video_file = SimpleUploadedFile(
            "test_clip.mp4", b"fake-video-bytes", content_type="video/mp4"
        )

        response = self.client_auth.post(
            "/api/videos/",
            {"title": "Clip con thumb", "file": video_file, "tag": "clutch"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica che il thumbnail è stato salvato nel DB
        from cs_clips.models import Video

        video = Video.objects.get(id=response.data["id"])
        self.assertTrue(video.thumbnail, "Il campo thumbnail dovrebbe essere popolato")
        self.assertIn("thumbnails/", video.thumbnail.name)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_video_detail_returns_thumbnail_url(self, mock_minio):
        """Video detail ritorna thumbnail_url nel payload."""

        def mock_presigned(bucket, name, expires=None, response_headers=None):
            if "thumbnails/" in name:
                return MOCK_THUMBNAIL_URL
            return MOCK_FILE_URL

        mock_minio.return_value.presigned_get_object.side_effect = mock_presigned

        # Crea video con thumbnail
        video = create_sample_video(self.user, title="Con Thumb")
        from django.core.files.base import ContentFile

        video.thumbnail.save(
            "thumbnails/test_thumb.jpg",
            ContentFile(b"\xff\xd8\xff\xe0fake-jpeg"),
            save=True,
        )

        response = self.client_auth.get(f"/api/videos/{video.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("thumbnail_url", response.data)
        self.assertEqual(response.data["thumbnail_url"], MOCK_THUMBNAIL_URL)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_video_without_thumbnail_returns_null(self, mock_minio):
        """Video senza thumbnail ritorna thumbnail_url: null."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        video = create_sample_video(self.user, title="Senza Thumb")

        response = self.client_auth.get(f"/api/videos/{video.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("thumbnail_url", response.data)
        self.assertIsNone(response.data["thumbnail_url"])

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_upload_succeeds_even_if_thumbnail_fails(self, mock_vfc, mock_minio):
        """Upload non fallisce se generazione thumbnail fallisce (graceful fallback)."""
        mock_clip = MagicMock()
        mock_clip.duration = 30
        mock_clip.__enter__ = MagicMock(return_value=mock_clip)
        mock_clip.__exit__ = MagicMock(return_value=False)
        # save_frame lancia eccezione
        mock_clip.save_frame.side_effect = RuntimeError("ffmpeg error")
        mock_vfc.return_value = mock_clip

        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL

        from django.core.files.uploadedfile import SimpleUploadedFile

        video_file = SimpleUploadedFile(
            "test_clip.mp4", b"fake-video-bytes", content_type="video/mp4"
        )

        response = self.client_auth.post(
            "/api/videos/",
            {"title": "Clip senza thumb", "file": video_file, "tag": "funny"},
            format="multipart",
        )

        # Upload deve riuscire anche se thumbnail fallisce
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        from cs_clips.models import Video

        video = Video.objects.get(id=response.data["id"])
        self.assertFalse(
            bool(video.thumbnail),
            "Thumbnail non dovrebbe essere presente se generazione fallita",
        )


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestVideoPublicRetrieve(APITestCase):
    """Test accesso pubblico a GET /api/videos/{id}/ per SSR e condivisione (AC-3)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.author = create_authenticated_user("author")
        self.video = create_sample_video(self.author, title="Clip Pubblica")

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_unauthenticated_retrieve_returns_200(self, mock_minio):
        """Visitatore non autenticato può accedere a /api/videos/{id}/ → 200."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get(f"/api/videos/{self.video.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Clip Pubblica")
        self.assertIn("thumbnail_url", response.data)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_unauthenticated_list_still_requires_auth(self, mock_minio):
        """Lista video richiede ancora autenticazione → 401."""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/videos/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
